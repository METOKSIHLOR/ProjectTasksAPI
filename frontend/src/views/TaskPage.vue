<script setup>
import {ref, watch, computed, onMounted, onBeforeUnmount, reactive, nextTick} from 'vue'
import { useRoute, useRouter } from 'vue-router'
import DashboardLayout from '../components/Layout.vue'
import BaseButton from '../components/BaseButton.vue'
import BaseCard from '../components/BaseCard.vue'
import BaseLoader from '../components/BaseLoader.vue'
import ModalWindow from '../components/ModalWindow.vue'
import BaseForm from '../components/BaseForm.vue'
import {getTask, getComments, createComment, deleteComment, updateTask, getProject} from '../api/api.js'
import { currentUser } from '../store/auth_store.js'
import * as yup from 'yup'

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
import {alertError, alertInfo, parseApiError} from "../store/alert_store.js";
import {connectWS, subscribe, unsubscribe} from '../api/ws'

/* router */
const router = useRouter()
const route = useRoute()

/* route state */
const projectId = ref(route.params.projectId)
const taskId = ref(route.params.taskId)

/* data */
const task = ref({})
const comments = ref([])

/* ui state */
const loading = ref(true)
const layoutRef = ref(null)
let socket = null

/* modals */
const showRenameTask = ref(false)
const showEditDescription = ref(false)

/* forms */
const commentForm = [{ name: 'text', type: 'textarea', label: '', placeholder: 'Write comment...' }]
const renameTaskForm = [{ name: 'title', label: 'Task title', placeholder: 'Task title', value: '' }]
const editDescriptionForm = [{ name: 'description', label: 'Description', placeholder: 'Task description', type: 'textarea', value: '' }]

// Схема валидации для переименования задачи и изменения описания
const commentSchema = yup.object({
  text: yup
      .string()
      .min(1, 'Comment must be at least 1 character')
      .max(500, 'Comment must be at most 500 characters')
      .required('Empty field'),
})
const editTaskSchema = yup.object({
  title: yup
      .string()
      .min(1, 'Task title must be at least 1 character')
      .max(25, 'Task title must be at most 25 characters')
      .required('Task title is required'),
})
const editDescriptionSchema = yup.object({
  description: yup
      .string()
      .min(1, 'Task description must be at least 1 character')
      .max(200, 'Task description must be at most 200 characters')
      .required('Task description is required')
})



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
/* access */
const isProjectOwner = computed(() =>
    task.value?.project_owner_email === currentUser.value?.email
)

/* task actions */
async function renameTask({ data, onSuccess, onError }) {
  try {
    await updateTask(projectId.value, taskId.value, { title: data.title })
    onSuccess()
    task.value.title = data.title
    showRenameTask.value = false
    alertInfo(
        'Done',
        `Task renamed to "${data.title}"`
    )
  }
  catch (err) {
    onError()
    const { title, message } = parseApiError(err)
    alertError(title, message)
  }
}

async function editDescription({ data, onSuccess, onError }) {
  try {
    await updateTask(projectId.value, taskId.value, { description: data.description })
    onSuccess()
    task.value.description = data.description
    showEditDescription.value = false
    alertInfo(
        'Done',
        `Description saved`
    )
  }
  catch (err) {
    onError()
    const { title, message } = parseApiError(err)
    alertError(title, message)
  }
}

/* comments */
async function addComment({ data, onSuccess, onError }) {
  try {
    const text = data.text?.trim()
    if (!text) return
    const newC = await createComment(projectId.value, taskId.value, {text: text, replied_to: REPLY.id})
    cancelReply()
    comments.value.push(newC)
    onSuccess()
    await layoutRef.value?.scrollToBottomSmooth()
  }
  catch (err) {
    const { title, message } = parseApiError(err)
    alertError(title, message)
    onError()
  }
}
async function addStatusComment(statusKey) {
  const text = buildStatusComment(statusKey)
  const newC = await createComment(projectId.value, taskId.value, {text: text, replied_to: null})
  newC.statusKey = statusKey
  comments.value.push(newC)
  await layoutRef.value?.scrollToBottomSmooth()
}
async function WS_addComment(msg) {
  if (msg?.author_email === currentUser.value?.email) return

  comments.value.push({
    id: msg.comment_id,
    text: msg.text,
    author_email: msg.author_email,
    author_name: msg.author_name,
    replied_to: msg.replied_to,
    created_at: msg.created_at,
    statusKey: parseStatusFromComment(msg.text)
  })

  await layoutRef.value?.scrollToBottomSmooth()
}

async function removeComment(comment) {
  try {
    if (!canDelete(comment)) return
    await deleteComment(projectId.value, taskId.value, comment.id)
    if (REPLY.id === comment.id) cancelReply()
    comments.value = comments.value.filter(c => c.id !== comment.id)
  }
  catch (err) {
    const { title, message } = parseApiError(err)
    alertError(title, message)
  }
}
function WS_removeComment(msg) {
  comments.value = comments.value.filter(comment => comment.id !== msg.comment_id)
}

const REPLY = reactive({
  id: null,
  author: null,
  text: null,
})
const formRef = ref(null)
async function createReply(id) {
  REPLY.id = comments.value.find(c => c.id === id).id;
  REPLY.author = comments.value.find(c => c.id === id).author_name;
  REPLY.text = comments.value.find(c => c.id === id).text;

  await layoutRef.value?.scrollToBottomSmooth();
  console.log(formRef.value)
  formRef.value?.setFocus()
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
function getReplyText(id) {
  if (id === null) return
  return comments.value.find(c => c.id === id)?.text
}
function getReplyName(id) {
  if (id === null) return
  return comments.value.find(c => c.id === id)?.author_name || null
}
function cancelReply() {
  REPLY.id = null
  REPLY.text = null
  REPLY.author = null
}
function scrollToComment(commentId) {
  const commentElement = document.getElementById(commentId);
  setTimeout(() => {
    commentElement.classList.remove('reply-active');
  }, 1000);
  if (commentElement) {
    commentElement.classList.add('reply-active')
    commentElement.scrollIntoView({
      behavior: 'smooth',
      block: 'center',
    });
  }
}

/* navigation */
function goBack() {
  router.push(`/projects/${projectId.value}`)
}

/* websocket */
async function handleTaskDeleteMessage(msg) {
    alertInfo(
        'Вжух!',
        `${msg.value?.name || ''}И задачи больше нет`
    )
    await router.push(`/projects/${projectId.value}`)
}

function handleCommentUpdateMessage(msg) {
  console.log('[TaskPage WS COMMENT UPDATE]', msg)
}

async function handleTaskMessage(event) {
  try {
    const msg = JSON.parse(event.data)

    switch (msg?.type) {
      case 'task_delete':
        await handleTaskDeleteMessage(msg)
        break

      case 'comment_create':
        await WS_addComment(msg)
        break

      case 'comment_update':
        handleCommentUpdateMessage(msg)
        break

      case 'comment_delete':
        WS_removeComment(msg)
        break
    }
  } catch (e) {
    console.warn('[TaskPage WS] failed to parse message')
  }
}

/* watch route */
watch(
    () => route.params,
    async (params, oldParams) => {
      if (socket && oldParams?.taskId && oldParams.taskId !== params.taskId) {
        unsubscribe(`task:${oldParams.taskId}`)
      }

      projectId.value = params.projectId
      taskId.value = params.taskId

      if (socket && oldParams?.taskId !== params.taskId) {
        subscribe(`task:${params.taskId}`)
      }

      await loadTaskAndComments()
    },
    { immediate: true }
)

onMounted(async () => {
  try {
    socket = await connectWS()
    subscribe(`task:${taskId.value}`)
    socket?.addEventListener('message', handleTaskMessage)
  }
  catch (err) {
    console.error('[TaskPage WS] failed to connect', err)
  }
})

onBeforeUnmount(() => {
  unsubscribe(`task:${taskId.value}`)
  socket?.removeEventListener('message', handleTaskMessage)
})
</script>

<template>
  <DashboardLayout ref="layoutRef">
    <!-- TITLE -->
    <template #title>
      <div class="page-title">
        <span>{{ task.title || 'Task not found' }}</span>

        <BaseButton
            v-if="task && isProjectOwner"
            class="edit-btn"
            @click="openRenameTask"
        >
          ✎
        </BaseButton>
      </div>
    </template>

    <template #header-center>
      <span
          class="task-status-label"
          :class="getStatusClass(task.status)"
          :style="{color: getStatusColor(task.status),borderColor: getStatusColor(task.status)}"
      >
          {{ getStatusText(task.status, 'full') || 'unknown status' }}
        </span>
    </template>

    <!-- HEADER -->
    <template #header>
      <BaseButton @click="goBack">
        ⮜ Back to Project
      </BaseButton>
    </template>

    <!-- TOP -->
    <template #content-top>
      <span class="task-description">
        <BaseButton
            v-if="task && isProjectOwner"
            class="edit-btn small"
            @click="openEditDescription"
        >
          ✎
        </BaseButton>

        <span class="desc-text">
          Description: {{ task.description || 'unknown' }}
        </span>
      </span>

      <div class="comments-header">
        <h3>Discussion</h3>
      </div>
    </template>

    <!-- COMMENTS -->
    <BaseLoader v-if="loading" />

    <div v-else class="list comments">
      <div v-if="comments.length === 0" class="list-empty">
        No comments yet.
      </div>
      <TransitionGroup name="comments">
        <BaseCard
            v-for="comment in comments"
            :key="comment.id"
            :id="comment.id"
            :type="getCardType(comment)"
            :clickable="false"
            :deletable="canDelete(comment)"
            :style="comment.statusKey ? { color: getStatusColor(comment.statusKey) } : null"
            @delete="removeComment(comment)"
            @reply="createReply(comment.id)"
        >
          <template #nickname v-if="showAuthor(comment) && !canDelete(comment)">
            {{ getDisplayName(comment) }}
          </template>

          <template #reply v-if="comment.replied_to">
            <span class="reply-author">{{ getReplyName(comment.replied_to) }}</span>
            <span class="reply-text" :class="getReplyText(comment.replied_to) ? '' : 'deleted'">
              {{getReplyText(comment.replied_to) || 'deleted comment'}}
            </span>

          </template>

          <span>
          <span v-if="comment.statusKey" class="status-changer">
            {{ statusAuthor(comment) }}
          </span>

          {{ displayText(comment) }}
        </span>
        </BaseCard>
      </TransitionGroup>
    </div>

    <!-- INPUT -->
    <template #content-bottom>

      <div class="add-comment">
        <div class="reply-block" v-if="REPLY.id" @click="scrollToComment(REPLY.id)">
          <span class="reply-text">
            <span class="reply-author">⮌ {{REPLY.author}}</span>
            <span>{{REPLY.text}}</span>
          </span>
          <button class="reply-cancel" @click="cancelReply">✕</button>
        </div>
        <BaseForm
            ref="formRef"
            :fields='commentForm'
            :schema="commentSchema"
            @submit="addComment"
            submitText="Send ➤"
            class="add-comment-form">

          <div v-if="canShowStatusButton" class="status-button-wrapper">
            <BaseButton :style="{'--status-color': getStatusButtonColor(task.status)}" @click="advanceStatus">
              {{ statusButtonText }}
            </BaseButton>
          </div>

        </BaseForm>
      </div>
    </template>

  </DashboardLayout>

  <!-- MODALS -->
  <ModalWindow v-if="showRenameTask" @close="showRenameTask=false">
    <h3 class="modal-title">Edit Task</h3>

    <BaseForm
        :fields="renameTaskForm"
        :schema="editTaskSchema"
        submitText="Save"
        @submit="renameTask"
    />
  </ModalWindow>

  <ModalWindow v-if="showEditDescription" @close="showEditDescription=false">
    <h3 class="modal-title">Edit Description</h3>

    <BaseForm
        :fields="editDescriptionForm"
        :schema="editDescriptionSchema"
        submitText="Save"
        @submit="editDescription"
    />
  </ModalWindow>

</template>

<style scoped>
.reply-block {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;

  margin-bottom: 2px;
  padding: 2px 6px;
  width: 100%;
  font-size: var(--font-size-base);
  font-style: italic;
  border-radius: 6px;
  border-left: 6px solid var(--color-primary);
  background: var(--color-primary-light);
  color: #333333;
  cursor: pointer;
}
.reply-active {
  animation: pulse 1s ease-in-out;
  background: var(--color-comment-bg) !important;
  box-shadow: 0 0 10px var(--color-primary) !important;
}
.reply-author {
  color: var(--color-primary);
  margin-right: 6px;
}
.reply-text {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  letter-spacing: 1.5px;
}
.deleted {
  color: orangered;
  font-style: italic;
}
.reply-cancel {
  color: #333333;
  border: none;
  font-style: normal;
  font-size: var(--font-size-base);
  cursor: pointer;
}
.reply-cancel:hover {
  color: #f44336;
}

.status-changer {
  font-weight: 400;
  color: var(--color-primary);
}

.task-description {
  word-wrap: anywhere;
  font-size: var(--font-size-base);
  color: var(--color-text-muted);
  font-weight: lighter;
  letter-spacing: initial;
}

.edit-btn.small {
  display: inline-block;
  vertical-align: middle;
  margin-bottom: 4px;
  width: calc(var(--font-size-base) + 2px);
  height: calc(var(--font-size-base) + 2px);
  font-size: calc(var(--font-size-base) - 6px);
  padding: 0;
}

.desc-text {
  vertical-align: middle;
  font-size: var(--font-size-base);
}

.comments-header {
  margin: 12px auto;
  display: flex;
  justify-content: center;
  font-size: var(--font-size-title);
}

.task-status-label {
  display: flex;
  align-items: center;

  font-size: var(--font-size-title);
  height: 100%;
  padding: 8px 16px;
  border-radius: 12px;
  font-weight: 500;
  border: 1px solid #ccc;
}

.list.comments {
  gap: 8px;
  margin-bottom: 0;
}

.add-comment {
  width: 100%;
  display: flex;
  flex-direction: column;
}

.add-comment-form {
  display: flex;
  flex-grow: 1;
  flex-direction: row !important;
}

.status-button-wrapper {
  flex-grow: 0;
  display: flex;
  justify-content: center;
  width: 108px;
}

.status-button-wrapper button {
  background: var(--color-bg);
  color: var(--status-color);
  border: 1px solid var(--status-color);
  transition: all 0.12s ease;
  font-weight: 600;
}

.status-button-wrapper button:hover {
  background: var(--status-color);
  color: #ffffff;
  border-color: var(--status-color);
}

/* COMMENTS TRANSITION GROUP */
.comments-enter-from {
  opacity: 0;
  transform: scale(0.5);
}
.comments-enter-active {
  transition: all 0.5s ease;
}
.comments-enter-to {
  opacity: 1;
  transform: scale(1);
}

/* Анимация удаления задачи */
.comments-leave-from {
  opacity: 1;
  transform: scale(1);
}
.comments-leave-active {
  position: absolute;
  transition: all 0.5s;
  pointer-events: none;
}
.comments-leave-to {
  opacity: 0;
  transform: scale(0.5);
}

/* Поднятие оставшихся */
.comments-move {
  transition: all 0.5s ease;
}

@keyframes pulse {
  0% {
    transform: scale(1);
    opacity: 1;
  }
  50% {
    transform: scale(1.1); /* Увеличение размера */
    opacity: 0.7; /* Плавное уменьшение прозрачности */
  }
  100% {
    transform: scale(1); /* Возвращение к исходному размеру */
    opacity: 1; /* Восстановление прозрачности */
  }
}
</style>
