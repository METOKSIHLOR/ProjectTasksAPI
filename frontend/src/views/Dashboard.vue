<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

import DashboardLayout from '../components/Layout.vue'
import BaseButton from '../components/BaseButton.vue'
import BaseCard from '../components/BaseCard.vue'
import ModalWindow from '../components/ModalWindow.vue'
import BaseForm from '../components/BaseForm.vue'
import BaseLoader from '../components/BaseLoader.vue'

import { getProjects, createProject, deleteProject } from '../api/api.js'
import {alertError, alertSuccess, parseApiError} from "../store/alert_store.js";

const router = useRouter()

// STATE
const projects = ref([])
const loading = ref(true)
const showCreateProject = ref(false)

// FORM
const projectForm = [
  {
    name: 'name',
    label: 'Project name',
    placeholder: 'Project name',
    value: ''
  }
]

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
async function addProject(data) {
  try {
    const newProject = await createProject({ name: data.name })
    projects.value.push(newProject)
    showCreateProject.value = false
    alertSuccess(
        'Success',
        `Project "${newProject?.name}" was successfully created`
    )
    await router.push(`/projects/${newProject.id}`)
  }
  catch (err) {
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

// INIT
onMounted(loadProjects)
</script>

<template>
  <DashboardLayout>

    <template #title>
      <span class="app-title">TasksAPI</span>
    </template>

    <template #content-top>
      <div class="projects-header">
        <h2>Your Projects</h2>

        <BaseButton @click="showCreateProject = true">
          Create project
        </BaseButton>
      </div>
    </template>

    <div class="projects-list">

      <BaseLoader v-if="loading" />

      <BaseCard v-else-if="projects.length === 0">
        No projects yet
      </BaseCard>

      <BaseCard
          v-for="project in projects"
          :key="project.id"
          clickable
          deletable
          @click="goToProject(project.id)"
          @delete="removeProject(project.id)"
      >
        {{ project.name }}
      </BaseCard>

    </div>

  </DashboardLayout>

  <ModalWindow
      v-if="showCreateProject"
      @close="showCreateProject = false"
  >
    <h3 class="modal-title">Create Project</h3>

    <BaseForm
        :fields="projectForm"
        submitText="Create project"
        @submit="addProject"
    />

  </ModalWindow>

</template>

<style scoped>
.projects-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: var(--font-size-title);
}
.projects-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.modal-title{
  margin-bottom:10px;
  font-size: var(--font-size-title);
}
.app-title {
  font-size: var(--font-size-title);
}
</style>