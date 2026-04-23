<script setup>
import {computed, nextTick, onMounted, ref, watch} from 'vue'
import { useRoute, useRouter } from 'vue-router'
import * as yup from 'yup'
import DashboardLayout from '../components/Layout.vue'
import BaseButton from '../components/BaseButton.vue'
import BaseCard from '../components/BaseCard.vue'
import ModalWindow from '../components/ModalWindow.vue'
import BaseForm from '../components/BaseForm.vue'
import BaseLoader from '../components/BaseLoader.vue'
import {
  getProject,
  getTasks,
  createTask,
  deleteTask,
  createProjectMember,
  deleteProjectMember,
  updateProject
} from '../api/api.js'
import { currentUser } from '../store/auth_store.js'
import { getStatusText, getStatusColor } from '../modules/statusModule.js'
import {alertError, alertInfo, alertSuccess, parseApiError} from "../store/alert_store.js";
import {subscribe} from '../api/ws'

const router = useRouter()
const route = useRoute()

// STATE
const projectId = ref(route.params.projectId)
const project = ref(null)
const tasks = ref([])
const members = ref([])
const isOwner = ref(false)
const loading = ref(true)

// MODALS
const showCreateTask = ref(false)
const showAddMember = ref(false)
const showRenameProject = ref(false)

const owner = computed(() =>
    members.value.find(m => m.role === 'owner')
)

// Ссылка на Layout
const layoutRef = ref(null)
const toggleCollapse = ref(true)

// Метод для вызова переключения
function toggleLayoutStretch() {
  layoutRef.value.toggleStretch()
  toggleCollapse.value = !toggleCollapse.value
}

// FORMS
const taskForm = [
  { name: 'title', label: 'Title', placeholder: 'Task title' },
  { name: 'description', label: 'Description', placeholder: 'Task description', type: 'textarea' },
  { name: 'assignee_email', label: 'Task performer', type: 'select', options: [] }
]
// Схема валидации для создания задачи в проекте
const createTaskSchema = yup.object({
  title: yup
      .string()
      .min(1, 'Title must be at least 1 character')
      .max(25, 'Title must be at most 25 characters')
      .required('Task title is required'),

  description: yup
      .string()
      .min(1, 'Description must be at least 1 character')
      .max(200, 'Description must be at most 200 characters')
      .required('Task description is required'),

  assignee_email: yup
      .string()
      .email('Invalid email format')
      .required('Performer email is required')
})

// Add member
const memberForm = [
  { name: 'email', label: 'User email', placeholder: 'User email' }
]
const addMemberSchema = yup.object({
  email: yup
      .string()
      .email('Invalid email format')  // Проверка на корректность формата почты
      .required('Email is required')  // Почта обязательна
})

// Rename project
const renameForm = [
  {
    name: 'name',
    label: 'Project name',
    placeholder: 'Project name',
    value: ''
  }
]
// Схема валидации для переименования проекта
const renameProjectSchema = yup.object({
  name: yup
      .string()
      .min(3, 'Project name must be at least 3 characters')
      .max(25, 'Project name must be at most 25 characters')
      .required('Project name is required')
})

// DATA LOADING
async function loadProject() {
  loading.value = true
  try {
    project.value = await getProject(projectId.value)
    members.value = project.value.members || []
    isOwner.value = members.value.some(
        m => m.email === currentUser.value?.email && m.role === 'owner'
    )
    tasks.value = await getTasks(projectId.value)

    const assigneeField = taskForm.find(f => f.name === 'assignee_email')
    assigneeField.options = members.value.map(m => ({
      label: `${m.name} (${m.email})`,
      value: m.email
    }))
    assigneeField.default = members.value.find(m => m.role === 'owner')?.email || ''
  }
  catch (err) {
    const { title, message } = parseApiError(err)
    alertError(title, message)

  } finally {
    loading.value = false
  }
}

// PROJECT ACTIONS
async function renameProject({ data, onSuccess, onError }) {
  try {
    await updateProject(projectId.value, { name: data.name })
    onSuccess()
    project.value.name = data.name
    showRenameProject.value = false
    alertInfo(
        'Done',
        `Project renamed to "${data.name}"`
    )
  }
  catch (err) {
    onError()
    const { title, message } = parseApiError(err)
    alertError(title, message)
  }
}

// TASK ACTIONS
async function addTask({ data, onSuccess, onError }) {
  if (!isOwner.value) return
  try {
    const payload = {
      title: data.title,
      description: data.description,
      assignee_email: data.assignee_email
    }
    const newTask = await createTask(projectId.value, payload)
    onSuccess()
    await router.push(`/projects/${projectId.value}/tasks/${newTask.id}`)
    showCreateTask.value = false
    alertSuccess(
        'Success',
        `Task "${data.title}" added`
    )
  }
  catch (err) {
    onError()
    const { title, message } = parseApiError(err)
    alertError(title, message)
  }
}
async function removeTask(id) {
  if (!isOwner.value) return
  try {
    await deleteTask(projectId.value, id)
    tasks.value = tasks.value.filter(t => t.id !== id)
    alertSuccess(
        'Success',
        `Task removed`
    )
  }
  catch (err) {
    const { title, message } = parseApiError(err)
    alertError(title, message)
  }
}

// MEMBER ACTIONS
async function addMember({ data, onSuccess, onError }) {
  if (!isOwner.value) return
  try {
    await createProjectMember(projectId.value, data.email)
    onSuccess()
    showAddMember.value = false
    alertSuccess(
        'Success',
        `Invite sent to "${data.email}"`
    )
  }
  catch (err) {
    onError()
    const { title, message } = parseApiError(err)
    alertError(title, message)
  }
}

async function removeMember(member) {
  if (!isOwner.value || member.email === currentUser.value?.email) return
  try {
    await deleteProjectMember(projectId.value, member.email)
    members.value = members.value.filter(m => m.email !== member.email)
    alertSuccess(
        'Success',
        `Member "${member?.name}" removed`
    )
  }
  catch (err) {
    const { title, message } = parseApiError(err)
    alertError(title, message)
  }
}

// NAVIGATION
function goBack() {
  router.push('/')
}
function goToTask(id) {
  router.push(`/projects/${projectId.value}/tasks/${id}`)
}

// HELPERS
function getMemberName(member) {
  return member.email === currentUser.value?.email
      ? currentUser.value?.name
      : member.name
}

// RELOAD ON ROUTE CHANGE
watch(
    () => route.params.projectId,
    async (id) => {
      projectId.value = id
      await loadProject()
    },
    { immediate: true }
)

function openRenameProject() {
  renameForm[0].value = project.value?.name || ''
  showRenameProject.value = true
}
onMounted(() => {
  subscribe(`project:${projectId.value}`)
})
</script>

<template>
  <DashboardLayout ref="layoutRef">
    <!-- TITLE -->
    <template #title>
      <div class="page-title">
        <span>{{ project?.name || 'Project not found' }}</span>

        <BaseButton
            v-if="project && isOwner"
            class="edit-btn"
            @click="openRenameProject"
        >
          ✎
        </BaseButton>
      </div>
    </template>

    <!-- HEADER -->
    <template #header>
      <BaseButton @click="goBack">⮜ Dashboard</BaseButton>
    </template>

    <!-- TOP CONTENT -->
    <template v-if="project" #content-top>
      <div class="list-header">
        <h2>Tasks</h2>
        <BaseButton v-if="isOwner && toggleCollapse" @click="showCreateTask=true">Create Task</BaseButton>
        <div v-if="!isOwner" class="owner-badge">
          By "{{ owner?.name }}" ({{ owner?.email }})
        </div>
      </div>
    </template>

    <!-- LOADING -->
    <BaseLoader v-if="loading" />

    <!-- TASK LIST -->
    <div v-else-if="project" :class="{'collapse': !toggleCollapse}" class="list">
      <div v-if="tasks.length === 0" class="list-empty">
        No tasks yet
      </div>

      <TransitionGroup name="task">
          <BaseCard
              v-for="task in tasks"
              :key="task.id"
              clickable
              :deletable="isOwner"
              @click="goToTask(task.id)"
              @delete="removeTask(task.id)"
          >
            <span>{{ task.title }}</span>

            <template #nickname>
          <span :style="{ color: getStatusColor(task.status) }">
            {{ getStatusText(task.status, 'full') }}
          </span>

              <span v-if="task.assignee_email === currentUser?.email">
            <b>Your task</b>
          </span>

              <span
                  v-else-if="isOwner"
                  class="task-owner"
              >
            For "{{ members.find(m => m.email === task.assignee_email)?.name }}"
          </span>
            </template>
          </BaseCard>
        </TransitionGroup>
    </div>

    <!-- MEMBERS HEADER -->
    <template #members-header v-if="isOwner && !loading">
      <div class="list-header">
        <h2 class="toggle">
          <BaseButton @click="toggleLayoutStretch">{{toggleCollapse ? '▲' : '▼'}}</BaseButton>
          <span>Project Members</span>
        </h2>
        <BaseButton v-if="!toggleCollapse" @click="showAddMember = true">Add Member</BaseButton>
      </div>
    </template>

    <!-- MEMBERS -->
    <template #content-bottom v-if="isOwner">
      <div :class="{'collapse': toggleCollapse}" class="list">
        <TransitionGroup name="task">
          <BaseCard
              v-for="member in members"
              :key="member.email"
              :deletable="member.email !== currentUser?.email"
              @delete="removeMember(member)"
          >
            <template #nickname>
              <span class="member-role">{{ member.role }}</span>
            </template>

            <div>
              <span>{{ getMemberName(member) }}</span>
              <span
                  v-if="member.email === currentUser?.email"
                  class="you-badge"
              >
              (you)
            </span>
            </div>
          </BaseCard>
        </TransitionGroup>

      </div>
    </template>
  </DashboardLayout>

  <!-- MODALS -->
  <ModalWindow v-if="showCreateTask" @close="showCreateTask = false">
    <h3 class="modal-title">New Task</h3>
    <BaseForm
        :fields="taskForm"
        :schema="createTaskSchema"
        submitText="Create task"
        @submit="addTask"
    />
  </ModalWindow>

  <ModalWindow v-if="showAddMember" @close="showAddMember = false">
    <h3 class="modal-title">New Member</h3>
    <BaseForm
        :fields="memberForm"
        :schema="addMemberSchema"
        submitText="Add Member"
        @submit="addMember"
    />
  </ModalWindow>

  <ModalWindow v-if="showRenameProject" @close="showRenameProject = false">
    <h3 class="modal-title">Rename Project</h3>
    <BaseForm
        :fields="renameForm"
        :schema="renameProjectSchema"
        submitText="Save"
        @submit="renameProject"
    />
  </ModalWindow>
</template>

<style scoped>
.collapse {
  height: 0;
  margin: 0;
  overflow: hidden;
}
.toggle {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

/* TASKS TRANSITION GROUP */
.task-enter-from {
  opacity: 0;
}
.task-enter-active {
  transition: all 0.5s ease;
}
.task-enter-to {
  opacity: 1;
}

/* Анимация удаления задачи */
.task-leave-from {
  opacity: 1;
  transform: scale(1);
}
.task-leave-active {
  position: absolute;
  width: 100%;
  transition: all 0.5s;
  pointer-events: none;
}
.task-leave-to {
  opacity: 0;
  transform: scale(1.2);
}

/* Поднятие оставшихся */
.task-move {
  transition: all 0.5s ease;
}


.owner-badge {
  color:var(--color-text-muted);
  font-style:italic;
}
.task-owner {
  color:#999;
}
.you-badge {
  color:var(--color-primary);
}
.member-role {
  color:#999;
}
</style>