<script setup>
import {computed, ref, watch} from 'vue'
import { useRoute, useRouter } from 'vue-router'

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

// FORMS
const taskForm = [
  { name: 'title', label: 'Title', placeholder: 'Task title' },
  { name: 'description', label: 'Description', placeholder: 'Task description', type: 'textarea' },
  { name: 'assignee_email', label: 'Assignee', type: 'select', options: [] }
]

// Add member
const memberForm = [
  { name: 'email', label: 'User email', placeholder: 'User email' }
]

// Rename project
const renameForm = [
  {
    name: 'name',
    label: 'Project name',
    placeholder: 'Project name',
    value: ''
  }
]

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
async function renameProject(data) {
  try {
    await updateProject(projectId.value, { name: data.name })
    project.value.name = data.name
    showRenameProject.value = false
    alertInfo(
        'Done',
        `Project renamed to "${data.name}"`
    )
  }
  catch (err) {
    const { title, message } = parseApiError(err)
    alertError(title, message)
  }
}

// TASK ACTIONS
async function addTask(data) {
  if (!isOwner.value) return
  try {
    const payload = {
      title: data.title,
      description: data.description,
      assignee_email: data.assignee_email
    }
    const newTask = await createTask(projectId.value, payload)
    await router.push(`/projects/${projectId.value}/tasks/${newTask.id}`)
    showCreateTask.value = false
    alertSuccess(
        '[200] success',
        `Task "${data.title}" added`
    )
  }
  catch (err) {
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
        '[200] success',
        `Task removed`
    )
  }
  catch (err) {
    const { title, message } = parseApiError(err)
    alertError(title, message)
  }
}

// MEMBER ACTIONS
async function addMember(data) {
  if (!isOwner.value) return
  try {
    await createProjectMember(projectId.value, data.email)
    showAddMember.value = false
    alertSuccess(
        '200 success',
        `Member "${data.email}" added`
    )
    await loadProject()
  }
  catch (err) {
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
        '200 success',
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
</script>

<template>
  <DashboardLayout>
    <!-- TITLE -->
    <template #title>
      <div class="project-title">
        <span>{{ project?.name || 'Project not found' }}</span>

        <button
            v-if="project && isOwner"
            class="edit-btn"
            @click="openRenameProject"
        >
          ✎
        </button>
      </div>
    </template>

    <!-- HEADER -->
    <template #header>
      <BaseButton @click="goBack">🠈 Dashboard</BaseButton>
    </template>

    <!-- TOP CONTENT -->
    <template v-if="project" #content-top>
      <div class="list-header">
        <h2>Tasks</h2>
        <BaseButton v-if="isOwner" @click="showCreateTask=true">Create Task</BaseButton>
        <div v-if="!isOwner" class="owner-badge">
          By "{{ owner?.name }}" ({{ owner?.email }})
        </div>
      </div>
    </template>

    <!-- LOADING -->
    <div v-if="loading" class="loader-wrapper">
      <BaseLoader />
    </div>

    <!-- TASK LIST -->
    <div v-else-if="project" class="list">
      <BaseCard v-if="tasks.length === 0">
        No tasks yet.
      </BaseCard>

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
    </div>

    <!-- MEMBERS -->
    <template v-if="isOwner">
      <div class="list-header">
        <h3>Project Members</h3>
        <BaseButton @click="showAddMember = true">Add Member</BaseButton>
      </div>

      <div class="list">
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
      </div>
    </template>
  </DashboardLayout>

  <!-- MODALS -->
  <ModalWindow v-if="showCreateTask" @close="showCreateTask = false">
    <h3 class="modal-title">New Task</h3>
    <BaseForm
        :fields="taskForm"
        submitText="Create task"
        @submit="addTask"
    />
  </ModalWindow>

  <ModalWindow v-if="showAddMember" @close="showAddMember = false">
    <h3 class="modal-title">New Member</h3>
    <BaseForm
        :fields="memberForm"
        submitText="Add Member"
        @submit="addMember"
    />
  </ModalWindow>

  <ModalWindow v-if="showRenameProject" @close="showRenameProject = false">
    <h3 class="modal-title">Rename Project</h3>
    <BaseForm
        :fields="renameForm"
        submitText="Save"
        @submit="renameProject"
    />
  </ModalWindow>
</template>

<style scoped>
.list-header {
  display:flex;
  justify-content:space-between;
  align-items:center;
  margin-bottom: 12px;
  font-size: var(--font-size-title);
}
.list {
  display:flex;
  flex-direction:column;
  gap:12px;
  margin-bottom: 24px;
}
.owner-badge {
  color:var(--color-primary-dark);
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
.project-title {
  display:flex;
  align-items:center;
  gap:8px;
  font-size: var(--font-size-title);
}
.edit-btn {
  width: calc(var(--font-size-title) + 6px);
  height: calc(var(--font-size-title) + 6px);
  font-size: calc(var(--font-size-title) - 8px);
  font-weight: normal;
  border-radius:50%;
  color:var(--color-primary);
  border:1px solid var(--color-primary);
  background:white;
  cursor:pointer;
  display:flex;
  align-items:center;
  justify-content:center;
}
.edit-btn:hover {
  background:var(--color-primary-light);
}
.loader-wrapper {
  display:flex;
  justify-content:center;
  margin-top:40px;
}

.modal-title{
  margin-bottom:10px;
  font-size: var(--font-size-title);
}
</style>