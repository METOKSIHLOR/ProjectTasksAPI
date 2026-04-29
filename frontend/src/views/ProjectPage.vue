<script setup>
import {computed, onBeforeUnmount, onMounted, ref, watch} from 'vue'
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
import {connectWS, getConnectionId, subscribe, unsubscribe} from '../api/ws'

const router = useRouter()
const route = useRoute()

// VARIABLES
const projectId = ref(route.params.projectId)
const project = ref(null)
const tasks = ref([])
const members = ref([])
const isOwner = ref(false)
const loading = ref(true)

const showCreateTask = ref(false)
const showAddMember = ref(false)
const showRenameProject = ref(false)

const layoutRef = ref(null)
const toggleCollapse = ref(true)
let socket = null

const owner = computed(() =>
    members.value.find(m => m.role === 'owner')
)

const taskForm = [
  { name: 'title', label: 'Title', placeholder: 'Task title' },
  { name: 'description', label: 'Description', placeholder: 'Task description', type: 'textarea' },
  { name: 'assignee_email', label: 'Task performer', type: 'select', options: [] }
]

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

const memberForm = [
  { name: 'email', label: 'User email', placeholder: 'User email' }
]

const addMemberSchema = yup.object({
  email: yup
      .string()
      .email('Invalid email format')
      .required('Email is required')
})

const renameForm = [
  {
    name: 'name',
    label: 'Project name',
    placeholder: 'Project name',
    value: ''
  }
]

const renameProjectSchema = yup.object({
  name: yup
      .string()
      .min(3, 'Project name must be at least 3 characters')
      .max(25, 'Project name must be at most 25 characters')
      .required('Project name is required')
})

// API
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
function WS_renameProject(msg) {
  if (!project.value) return
  if (msg.origin_connection_id === getConnectionId()) return

  project.value.name = msg.new_details

  alertInfo(
      'Attention!',
      `${owner.value?.name || 'Project owner'} updated Project Name`
  )
}

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
function WS_addTask(msg) {
  if (!project.value) return
  if (msg.origin_connection_id === getConnectionId()) return

  tasks.value.push({
    id: msg.task_id,
    title: msg.title,
    status: msg.status,
    assignee_email: msg.assignee_email
  })

  alertInfo(
      'Attention!',
      `${owner.value?.name || 'Project owner'} created a new task`
  )
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
function WS_removeTask(msg) {
  if (!project.value) return
  if (msg.origin_connection_id === getConnectionId()) return

  const deletingTask = tasks.value.find(task => task.id === msg.task_id)

  alertInfo(
      'Attention!',
      `${owner.value?.name || 'Project owner'} deleted a ${deletingTask.title} Task`
  )
  tasks.value = tasks.value.filter(task => task.id !== msg.task_id)
}

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
function WS_addMember(msg) {
  if (!project.value || !isOwner.value) return

  const memberExists = members.value.some(member => member.email === msg.user_email)
  if (memberExists) return

  members.value.push({
    email: msg.user_email,
    name: msg.user_name,
    role: msg.user_role
  })

  const assigneeField = taskForm.find(field => field.name === 'assignee_email')
  assigneeField?.options.push({
    label: `${msg.user_name} (${msg.user_email})`,
    value: msg.user_email
  })

  alertInfo(
      'Attention!',
      `${msg.user_name} joined the project`
  )
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
async function WS_removeMember(msg) {
  if (!project.value) return
  if (msg.origin_connection_id === getConnectionId()) return

  members.value = members.value.filter(m => m.email !== msg.member_email)

  const removedCurrentUser = msg.member_email === currentUser.value?.email
  if (removedCurrentUser) {
    alertInfo(
        'Вжух!',
        `и ${owner.value?.name || 'Project owner'} выгнал тебя из Проекта`
    )
    await router.push('/')
  }
  else {
    alertInfo(
        'Attention!',
        `${owner.value?.name || 'Project owner'} removed ${msg.member_email} from this Project`
    )
  }
}

//OTHER WEBSOCKETS
function WS_TaskUpdate(msg) {
  if (!project.value) return
  if (msg.origin_connection_id === getConnectionId()) return

  const taskIndex = tasks.value.findIndex(task => task.id === msg.task_id)
  if (
      taskIndex !== -1 &&
      typeof msg.new_details === 'object'
  ) {
    tasks.value[taskIndex] = {
      ...tasks.value[taskIndex],
      ...msg.new_details
    }
  }

  let actorName = owner.value?.name || 'Project owner'
  let actionText = 'updated a task'
  if ('status' in details) {
    actorName = getMemberNameByEmail(
        currentTask?.assignee_email
    )
    actionText = `changed ${currentTask?.title} Task status`
  }
  if ('title' in details) {
    actionText = `changed ${details.title} Task title`
  }
  if ('description' in details) {
    actionText = `changed ${currentTask?.title} Task description`
  }
  alertInfo(
      'Attention!',
      `${actorName} ${actionText}`
  )
}
async function WS_ProjectDelete(msg) {
  if (!project.value) return
  if (msg.origin_connection_id === getConnectionId()) return

  alertInfo(
      'Вжух!',
      `и ${owner.value?.name || 'Project owner'} удалил весь Проект`
  )
  await router.push('/')
}

// WS HANDLER
async function handleProjectMessage(event) {
  try {
    const msg = JSON.parse(event.data)

    switch (msg?.type) {
      case 'project_update':
        WS_renameProject(msg)
        break

      case 'task_create':
        WS_addTask(msg)
        break

      case 'task_update':
        WS_TaskUpdate(msg)
        break

      case 'task_delete':
        WS_removeTask(msg)
        break

      case 'invite_accept':
        WS_addMember(msg)
        break

      case 'member_remove':
        await WS_removeMember(msg)
        break

      case 'project_delete':
        await WS_ProjectDelete()
        break
    }
  } catch (error) {
    console.warn('[ProjectPage WS] failed to parse message')
    console.warn(error)
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
function toggleLayoutStretch() {
  layoutRef.value.toggleStretch()
  toggleCollapse.value = !toggleCollapse.value
}

function openRenameProject() {
  renameForm[0].value = project.value?.name || ''
  showRenameProject.value = true
}

function getMemberName(member) {
  return member.email === currentUser.value?.email
      ? currentUser.value?.name
      : member.name
}

function getMemberNameByEmail(email) {
  const member = members.value.find(m => m.email === email)
  return member?.email === currentUser.value?.email
      ? currentUser.value?.name
      : member?.name || email || 'Someone'
}

// WATCHERS
watch(
    () => route.params.projectId,
    async (id, oldId) => {
      if (socket && oldId && oldId !== id) {
        unsubscribe(`project:${oldId}`)
      }

      projectId.value = id

      if (socket && id && oldId !== id) {
        subscribe(`project:${id}`)
      }

      await loadProject()
    },
    { immediate: true }
)

// LIFECYCLE
onMounted(async () => {
  try {
    socket = await connectWS()
    subscribe(`project:${projectId.value}`)
    socket?.addEventListener('message', handleProjectMessage)
  }
  catch (err) {
    console.error('[ProjectPage WS] failed to connect', err)
  }
})

onBeforeUnmount(() => {
  unsubscribe(`project:${projectId.value}`)
  socket?.removeEventListener('message', handleProjectMessage)
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
