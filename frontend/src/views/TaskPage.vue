<script setup>
import { ref, watch, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'

/* UI */
import DashboardLayout from '../components/Layout.vue'
import BaseButton from '../components/BaseButton.vue'
import BaseCard from '../components/BaseCard.vue'
import BaseLoader from '../components/BaseLoader.vue'
import ModalWindow from '../components/ModalWindow.vue'
import BaseForm from '../components/BaseForm.vue'

/* API */
import {
  getTask,
  getComments,
  createComment,
  deleteComment,
  updateTask,
  getProject
} from '../api/api.js'

/* store */
import { currentUser } from '../store/auth_store.js'

/* status module */
import {
  buildStatusComment,
  isStatusComment,
  cleanStatusText,
  getNextStatus,
  getStatusButtonText,
  getStatusClass,
  getStatusColor,
  getStatusText,
  parseStatusFromComment,
  canAdvanceStatus,
  getStatusButtonColor
} from '../modules/statusModule.js'
import {alertError, alertInfo, alertSuccess, parseApiError} from "../store/alert_store.js";

/* router */
const router = useRouter()
const route = useRoute()

/* route state */
const projectId = ref(route.params.projectId)
const taskId = ref(route.params.taskId)

/* data */
const project = ref(null)
const task = ref({})
const comments = ref([])

/* ui state */
const loading = ref(true)
const newComment = ref('')
const layoutRef = ref(null)

/* modals */
const showRenameTask = ref(false)
const showEditDescription = ref(false)

/* forms */
const renameTaskForm = [{ name: 'title', label: 'Task title', placeholder: 'Task title', value: '' }]
const editDescriptionForm = [{ name: 'description', label: 'Description', placeholder: 'Task description', type: 'textarea', value: '' }]

/* access */
const isProjectOwner = computed(() =>
    project.value?.members?.some(
        m => m.email === currentUser.value?.email && m.role === 'owner'
    )
)

/* status ui */
const statusButtonText = computed(() =>
    getStatusButtonText(task.value?.status)
)
const canShowStatusButton = computed(() =>
    task.value?.assignee_email &&
    currentUser.value?.email === task.value.assignee_email &&
    canAdvanceStatus(task.value?.status)
)

/* modals */
function openRenameTask() {
  renameTaskForm[0].value = task.value?.title || ''
  showRenameTask.value = true
}
function openEditDescription() {
  editDescriptionForm[0].value = task.value?.description || ''
  showEditDescription.value = true
}

/* load */
async function loadTaskAndComments() {
  loading.value = true
  try {
    project.value = await getProject(projectId.value)
    task.value = await getTask(projectId.value, taskId.value) || {}
    comments.value = await getComments(projectId.value, taskId.value) || []
    comments.value.forEach(c => c.statusKey = parseStatusFromComment(c.text))
    if (!comments.value.some(c => isStatusComment(c.text))) {
      await addStatusComment('todo')
    }
  }
  catch (err) {
    const { title, message } = parseApiError(err)
    alertError(title, message)
  }
  finally {
    loading.value = false
    await layoutRef.value?.scrollToBottomInstant()
  }
}

/* task actions */
async function renameTask(data) {
  try {
    await updateTask(projectId.value, taskId.value, { title: data.title })
    task.value.title = data.title
    showRenameTask.value = false
    alertInfo(
        'Done',
        `Task renamed to "${data.title}"`
    )
  }
  catch (err) {
    const { title, message } = parseApiError(err)
    alertError(title, message)
  }
}

async function editDescription(data) {
  try {
    await updateTask(projectId.value, taskId.value, { description: data.description })
    task.value.description = data.description
    showEditDescription.value = false
    alertInfo(
        'Done',
        `Description saved`
    )
  }
  catch (err) {
    const { title, message } = parseApiError(err)
    alertError(title, message)
  }
}

/* comments */
async function addComment() {
  try {
    const text = newComment.value.trim()
    if (!text) return
    const newC = await createComment(projectId.value, taskId.value, text)
    comments.value.push(newC)
    newComment.value = ''
    await layoutRef.value?.scrollToBottomSmooth()
  }
  catch (err) {
    const { title, message } = parseApiError(err)
    alertError(title, message)
  }
}

async function addStatusComment(statusKey) {
  const text = buildStatusComment(statusKey)
  const newC = await createComment(projectId.value, taskId.value, text)
  newC.statusKey = statusKey
  comments.value.push(newC)
  await layoutRef.value?.scrollToBottomSmooth()
}

async function removeComment(comment) {
  try {
    if (!canDelete(comment)) return
    await deleteComment(projectId.value, taskId.value, comment.id)
    comments.value = comments.value.filter(c => c.id !== comment.id)
  }
  catch (err) {
    const { title, message } = parseApiError(err)
    alertError(title, message)
  }
}

/* status */
async function advanceStatus() {
  try {
    const newStatus = getNextStatus(task.value.status)
    if (!newStatus) return
    await updateTask(projectId.value, taskId.value, { status: newStatus })
    task.value.status = newStatus
    await addStatusComment(newStatus)
  }
  catch (err) {
    const { title, message } = parseApiError(err)
    alertError(title, message)
  }
}

/* helpers */
function getCardType(comment) {
  if (isStatusComment(comment.text)) return 'status'
  if (comment.author_email === currentUser.value?.email) return 'comment-owner'
  return 'comment-companion'
}

function canDelete(comment) {
  return !isStatusComment(comment.text) && comment.author_email === currentUser.value?.email
}

function displayText(comment) {
  return cleanStatusText(comment.text)
}

function showAuthor(comment) {
  return !isStatusComment(comment.text)
}

function statusAuthor(comment) {
  return isStatusComment(comment.text) ? getDisplayName(comment) : ''
}

function getDisplayName(comment) {
  return comment.author_email === currentUser.value?.email
      ? currentUser.value?.name
      : comment.author_name
}

/* submit */
function handleCommentKeydown(event) {
  if (event.key !== 'Enter') return
  if (event.shiftKey) {
    return
  }

  event.preventDefault()
  addComment()
}

/* navigation */
function goBack() {
  router.push(`/projects/${projectId.value}`)
}

/* watch route */
watch(
    () => route.params,
    params => {
      projectId.value = params.projectId
      taskId.value = params.taskId
      loadTaskAndComments()
    },
    { immediate: true }
)
</script>

<template>
  <DashboardLayout ref="layoutRef">
    <!-- TITLE -->
    <template #title>
      <div class="task-title">
        <span>{{ task.title || 'Task not found' }}</span>

        <button
            v-if="task && isProjectOwner"
            class="edit-btn"
            @click="openRenameTask"
        >
          ✎
        </button>

        <span
            class="task-status-label"
            :class="getStatusClass(task.status)"
            :style="{color: getStatusColor(task.status),borderColor: getStatusColor(task.status)}"
        >
          {{ getStatusText(task.status, 'full') || 'unknown status' }}
        </span>
      </div>
    </template>

    <!-- HEADER -->
    <template #header>
      <BaseButton @click="goBack">
        🠈 Back to Project
      </BaseButton>
    </template>

    <!-- TOP -->
    <template #content-top>
      <span class="task-description">
        <span class="desc-text">
          Description: {{ task.description || 'unknown' }}
        </span>

        <button
            v-if="task && isProjectOwner"
            class="edit-btn small"
            @click="openEditDescription"
        >
          ✎
        </button>
      </span>

      <div class="tasks-header">
        <h3>Discussion</h3>
      </div>
    </template>

    <!-- COMMENTS -->
    <div v-if="loading" class="loader-wrapper">
      <BaseLoader />
    </div>

    <div v-else class="list">
      <BaseCard v-if="comments.length === 0">
        No comments yet.
      </BaseCard>

      <BaseCard
          v-for="comment in comments"
          :key="comment.id"
          :type="getCardType(comment)"
          :clickable="false"
          :deletable="canDelete(comment)"
          :style="comment.statusKey ? { color: getStatusColor(comment.statusKey) } : null"
          @delete="removeComment(comment)"
      >
        <template #nickname v-if="showAuthor(comment)">
          {{ getDisplayName(comment) }}
        </template>

        <span>
          <span v-if="comment.statusKey" class="status-changer">
            {{ statusAuthor(comment) }}
          </span>

          {{ displayText(comment) }}
        </span>
      </BaseCard>
    </div>

    <!-- INPUT -->
    <template #content-bottom>
      <form @submit.prevent="addComment" class="add-comment-form">
        <textarea
            class="comment-area"
            v-model="newComment"
            placeholder="Write a comment..."
            rows="2"
            @keydown="handleCommentKeydown"
        />

        <BaseButton type="submit">
          Send
        </BaseButton>
      </form>

      <div
          v-if="canShowStatusButton"
          class="status-button-wrapper"
      >
        <BaseButton
            :style="{'--status-color': getStatusButtonColor(task.status)}"
            @click="advanceStatus"
        >
          {{ statusButtonText }}
        </BaseButton>
      </div>
    </template>

  </DashboardLayout>

  <!-- MODALS -->
  <ModalWindow
      v-if="showRenameTask"
      @close="showRenameTask=false"
  >
    <h3 class="modal-title">
      Edit Task
    </h3>

    <BaseForm
        :fields="renameTaskForm"
        submitText="Save"
        @submit="renameTask"
    />
  </ModalWindow>

  <ModalWindow
      v-if="showEditDescription"
      @close="showEditDescription=false"
  >
    <h3 class="modal-title">
      Edit Description
    </h3>

    <BaseForm
        :fields="editDescriptionForm"
        submitText="Save"
        @submit="editDescription"
    />
  </ModalWindow>

</template>

<style scoped>
.status-changer {
  font-weight: 400;
  color: var(--color-primary);
  margin-right: 4px;
}

.modal-title{
  margin-bottom:10px;
  font-size: var(--font-size-title);
}
.task-description {
  word-wrap: anywhere;
  font-size: 16px;
  color: var(--color-text);
  font-weight: lighter;
  letter-spacing: initial;
}
.comment-area {
  background: var(--color-card);
  color: var(--color-text);
  border: 1px solid var(--color-primary-light);
  outline-color: var(--color-primary);
}
.task-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: var(--font-size-title);
}
.edit-btn {
  width: calc(var(--font-size-title) + 6px);
  height: calc(var(--font-size-title) + 6px);
  font-size: calc(var(--font-size-title) - 8px);
  border-radius: 50%;
  border: 1px solid var(--color-primary);
  background: var(--color-card);
  color: var(--color-text);
  font-weight: normal;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: 0.15s;
}

.edit-btn.small {
  display: inline-block;
  vertical-align: middle;
  margin-left: 6px;
  width: calc(var(--font-size-base) + 4px);
  height: calc(var(--font-size-base) + 4px);
  font-size: calc(var(--font-size-base) - 6px);
}

.desc-text {
  vertical-align: middle;
  font-size: var(--font-size-base);
}

.edit-btn:hover {
  background: var(--color-primary-dark);
  color: var(--color-primary-light);
}

.tasks-header {
  margin: 12px auto;
  display: flex;
  justify-content: center;
  font-size: var(--font-size-title);
}

.task-status-label {
  padding: 4px 10px;
  border-radius: 12px;
  font-weight: 500;
  border: 1px solid #ccc;
}

.list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.list .base-card {
  padding: 6px 18px;
  border-radius: 18px;
}

.add-comment-form {
  display: flex;
  flex-direction: row;
  gap: 8px;
}

.add-comment-form textarea {
  flex-grow: 1;
  padding: 8px 10px;
  border-radius: 6px;
  border: 1px solid #ccc;
  resize: none;
}

.status-button-wrapper {
  width: 100%;
  display: flex;
  justify-content: center;
}

.status-button-wrapper button {
  width: 100%;
  background: #ffffff;
  color: var(--status-color);
  border: 1px solid var(--status-color);
  transition: background 0.15s, color 0.15s, border-color 0.15s;
  font-weight: 600;
  letter-spacing: 0.2px;
}

.status-button-wrapper button:hover {
  background: var(--status-color);
  color: #ffffff;
  border-color: var(--status-color);
}

.loader-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 40px;
}
</style>