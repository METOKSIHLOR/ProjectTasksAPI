<script setup>
import {ref, onBeforeUnmount, onMounted} from 'vue'
import { useRouter } from 'vue-router'

import DashboardLayout from '../components/Layout.vue'
import BaseButton from '../components/BaseButton.vue'
import BaseCard from '../components/BaseCard.vue'
import ModalWindow from '../components/ModalWindow.vue'
import BaseForm from '../components/BaseForm.vue'
import BaseLoader from '../components/BaseLoader.vue'
import * as yup from 'yup'
import { getProjects, createProject, deleteProject } from '../api/api.js'
import {alertError, alertInfo, alertSuccess, parseApiError} from "../store/alert_store.js";
import {currentUser} from "../store/auth_store.js";
import {connectWS, getConnectionId} from '../api/ws'

const router = useRouter()

// STATE
const projects = ref([])
const loading = ref(true)
const showCreateProject = ref(false)
let socket = null

// FORM
const projectForm = [
  {
    name: 'name',
    label: 'Project name',
    placeholder: 'Project name',
    value: ''
  }
]
// Схема валидации для создания проекта
const createProjectSchema = yup.object({
  name: yup
      .string()
      .min(3, 'Project name must be at least 3 characters')  // Минимум 3 символа
      .max(25, 'Project name must be at most 25 characters')  // Максимум 25 символов
      .required('Project name is required')  // Название обязательно
})

// LOAD PROJECTS
async function loadProjects() {
  loading.value = true
  try {
    const data = await getProjects()
    projects.value = Array.isArray(data) ? data : []
  }
  catch (err) {
    const { title, message } = parseApiError(err)
    alertError(title, message)

  } finally {
    loading.value = false
  }
}

// PROJECT ACTIONS
async function addProject({ data, onSuccess, onError }) {
  try {
    const newProject = await createProject({ name: data.name })
    onSuccess()
    projects.value.push(newProject)
    showCreateProject.value = false
    alertSuccess(
        'Success',
        `Project "${newProject?.name}" was successfully created`
    )
    await router.push(`/projects/${newProject.id}`)
  }
  catch (err) {
    onError()
    const { title, message } = parseApiError(err)
    alertError(title, message)
  }
}
async function removeProject(id) {
  try {
    const project = projects.value.find(p => p.id === id)
    await deleteProject(id)
    projects.value = projects.value.filter(p => p.id !== id)
    alertSuccess(
        'Success',
        `Project "${project?.name}" removed`
    )
  }
  catch (err) {
    const { title, message } = parseApiError(err)
    alertError(title, message)
  }
}

// NAVIGATION
const goToProject = (id) => router.push(`/projects/${id}`)

// WEBSOCKET
function handleMemberKickedMessage(msg) {
  if (msg.origin_connection_id === getConnectionId()) return

  const project = projects.value.find(project => project.id === msg.project_id)
  if (!project) return

  projects.value = projects.value.filter(project => project.id !== msg.project_id)

  alertInfo(
      'Attention!',
      `You were removed from project "${project.name}"`
  )
}

async function handleDashboardMessage(event) {
  try {
    const msg = JSON.parse(event.data)

    switch (msg?.type) {
      case 'member_kicked':
        handleMemberKickedMessage(msg)
        break
    }
  } catch (error) {
    console.warn('[Dashboard WS] failed to parse message')
  }
}

// INIT
onMounted(async () => {
  await loadProjects()

  try {
    socket = await connectWS()
    socket?.addEventListener('message', handleDashboardMessage)
  }
  catch (err) {
    console.error('[Dashboard WS] failed to connect', err)
  }
})

onBeforeUnmount(() => {
  socket?.removeEventListener('message', handleDashboardMessage)
})
</script>

<template>
  <DashboardLayout>

    <template #title>
      <span class="page-title">TasksAPI</span>
    </template>

    <template #content-top>
      <div class="list-header">
        <h2>Your Projects</h2>

        <BaseButton @click="showCreateProject = true">
          Create project
        </BaseButton>
      </div>
    </template>

    <div class="list">

      <BaseLoader v-if="loading" />

      <div v-else-if="projects.length === 0" class="list-empty">
        No projects yet
      </div>

      <TransitionGroup name="projects">
        <BaseCard
            v-for="project in projects"
            :key="project.id"
            clickable
            :deletable="project?.owner_email === currentUser?.email"
            @click="goToProject(project.id)"
            @delete="removeProject(project.id)"
        >
          <span class="project">
            {{ project.name }}
            <span v-if="project?.owner_email !== currentUser?.email" class="owner">By {{project.owner_email}}</span>
            <span v-else class="your-project">Your Project</span>
          </span>
        </BaseCard>
      </TransitionGroup>
    </div>

  </DashboardLayout>

  <ModalWindow v-if="showCreateProject" @close="showCreateProject = false">
    <h3 class="modal-title">Create Project</h3>

    <BaseForm
        :fields="projectForm"
        :schema="createProjectSchema"
        submitText="Create project"
        @submit="addProject"
    />
  </ModalWindow>

</template>

<style scoped>
.project {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
}
.owner {
  color: var(--color-text-muted);
  font-style: italic;
}
.your-project {
  color: var(--color-primary);
  font-weight: bold;
}

/* PROJECTS TRANSITION GROUP */
.projects-enter-from {
  opacity: 0;
}
.projects-enter-active {
  transition: all 0.5s ease;
}
.projects-enter-to {
  opacity: 1;
}

/* Анимация удаления задачи */
.projects-leave-from {
  opacity: 1;
  transform: scale(1);
}
.projects-leave-active {
  position: absolute;
  width: 100%;
  transition: all 0.5s;
  pointer-events: none;
}
.projects-leave-to {
  opacity: 0;
  transform: scale(1.2);
}

/* Поднятие оставшихся */
.projects-move {
  transition: all 0.5s ease;
}
</style>
