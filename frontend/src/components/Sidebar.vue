<script setup>
import {defineProps, onBeforeUnmount, onMounted, ref, watch} from 'vue';
import { useRouter } from 'vue-router';
import {clearCurrentUser, currentUser} from '../store/auth_store.js';
import ModalWindow from './ModalWindow.vue';
import BaseForm from './BaseForm.vue';
import {alertError, alertInfo, alertSuccess, parseApiError} from '../store/alert_store.js';
import {apiAcceptInvite, apiDeclineInvite, getUserInvites, logoutUser, updateCurrentUserName} from '../api/api.js';
import BaseButton from "./BaseButton.vue";
import BaseCard from "./BaseCard.vue";
import BaseLoader from "./BaseLoader.vue";
import {connectWS} from '../api/ws'
import * as yup from 'yup'

const props = defineProps({
  menuOpen: {
    type: Boolean,
    required: true
  },
  closeMenu: {
    type: Function,
    required: true
  }
});

const router = useRouter();

// Поле для ввода нового имени
const EditNameForm = [
  {
    name: 'newName',
    label: 'New Name',
    type: 'text',
    placeholder: 'Enter your new name',
    value: ''
  }
];
// Схема валидации для смены имени и почты
const EditNameSchema = yup.object({
  newName: yup
      .string()
      .min(3, 'Name must be at least 3 characters')
      .max(25, 'Comment must be at most 25 characters')
      .required('Name is required')
})

/* modal state */
const showInvites = ref(false)
const showChangeName = ref(false)

const invitesLoading = ref(false)
const invites = ref([])
let socket = null

async function loadInvites() {
  showInvites.value = true
  invitesLoading.value = true

  try {
    invites.value = await getUserInvites()
  }
  catch (err) {
    const { title, message } = parseApiError(err)
    alertError(title, message)
  }
  finally {
    invitesLoading.value = false
  }
}

async function refreshInvites() {
  try {
    invites.value = await getUserInvites()
  }
  catch (err) {
    const { title, message } = parseApiError(err)
    alertError(title, message)
  }
}

async function acceptInvite(inviteId, projectId) {
  try {
    await apiAcceptInvite(inviteId);
    alertInfo('Done', `Welcome to Project`);
    await router.push(`/projects/${projectId}`);
  } catch (err) {
    const { title, message } = parseApiError(err);
    alertError(title, message);
  }
}

async function declineInvite(inviteId) {
  try {
    await apiDeclineInvite(inviteId);
    alertInfo('Done', `Invite Declined`);
    invites.value = invites.value.filter(invite => invite.id !== inviteId);
  } catch (err) {
    const { title, message } = parseApiError(err);
    alertError(title, message);
  }
}

// Функция обновления имени
async function submitNameChange({ data, onSuccess, onError }) {
  const newName = data.newName.trim();

  try {
    await updateCurrentUserName(newName);
    onSuccess()
    currentUser.value.name = newName;
    showChangeName.value = false;
    alertSuccess('Success', `Name changed. Hello, ${newName}`);
  }
  catch (err) {
    onError()
    const { title, message } = parseApiError(err);
    alertError(title, message);
  }
}

// Выход из системы
async function handleLogout() {
  try {
    await logoutUser();
    clearCurrentUser();
    await router.push('/login');
  } catch (err) {
    const { title, message } = parseApiError(err);
    alertError(title, message);
  }
}


const showEmptyState = ref(true)
function handleAfterLeave() {
  if (!invites.value.length) {
    showEmptyState.value = true
  }
}
watch(invites, (val) => {
  if (val.length > 0) {
    showEmptyState.value = false
  }
})

function handleInviteCreateMessage(msg) {
  alertInfo('Attention!', 'You received a new project invite')
  refreshInvites()
}

async function handleUserMessage(event) {
  try {
    const msg = JSON.parse(event.data)

    switch (msg?.type) {
      case 'invite_create':
        handleInviteCreateMessage(msg)
        break
    }
  } catch (e) {
    console.warn('[Sidebar WS] failed to parse message')
  }
}

onMounted(async () => {
  try {
    socket = await connectWS()
    socket?.addEventListener('message', handleUserMessage)
  }
  catch (err) {
    console.error('[Sidebar WS] failed to connect', err)
  }
})

onBeforeUnmount(() => {
  socket?.removeEventListener('message', handleUserMessage)
})
</script>

<template>
  <div>
    <div v-if="menuOpen" class="drawer-overlay" @click="closeMenu"></div>

    <div class="drawer" :class="{ open: menuOpen }">
      <div class="drawer-header">
        <span class="drawer-title">{{ currentUser?.name }}</span>
        <button class="drawer-close" @click="closeMenu">✕</button>
      </div>

      <div class="drawer-content">
        <button class="drawer-item" @click="closeMenu(); loadInvites()">+ Invites</button>
        <button class="drawer-item" @click="showChangeName = true; closeMenu()">✎ Change Name</button>
        <button class="drawer-item">✎ {{ currentUser?.email }}</button>
        <button class="drawer-item">✎ Change Password</button>
        <button class="drawer-item" @click="router.push('/settings'); closeMenu()">⛭ Settings</button>
        <button class="drawer-item logout" @click="handleLogout">🠈 Log Out</button>
      </div>
    </div>

    <!-- Modal for change name -->
    <ModalWindow v-if="showChangeName" @close="showChangeName=false">
      <h3 class="modal-title">Change your name, <span style="color: var(--color-primary)">{{currentUser.name}}</span></h3>

      <BaseForm
          :fields="EditNameForm"
          :schema="EditNameSchema"
          @submit="submitNameChange"
          submitText="Confirm"
      />
    </ModalWindow>

    <ModalWindow v-if="showInvites" @close="showInvites=false">
      <h3 class="modal-title">Current invites</h3>
      <BaseLoader v-if="invitesLoading" />

      <div v-else-if="showEmptyState" class="list-empty">
        No invites
      </div>

      <div class="invites-list">
        <TransitionGroup name="invite" @after-leave="handleAfterLeave">
          <div key="invite-anchor" class="anchor"></div>
            <BaseCard
                v-for="inv in invites"
                :key="inv.id"
            >
              <template #nickname>
                <span>Project {{ inv.project_name }}</span>
                <span style="font-style: italic">Author: {{ inv.project_author_email }}</span>
              </template>

              <div class="invite-actions">
                <BaseButton
                    class="inv-btn accept"
                    @click="acceptInvite(inv.id, inv.project_id)"
                >
                  ✓
                </BaseButton>
                <BaseButton
                    class="inv-btn decline"
                    @click="declineInvite(inv.id)"
                >
                  ✕
                </BaseButton>
              </div>
            </BaseCard>
          </TransitionGroup>
      </div>
    </ModalWindow>
  </div>
</template>

<style scoped>
.drawer-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.25);
  backdrop-filter: blur(4px);
  z-index: 10;
}
.drawer {
  position: fixed;
  top: 0;
  right: 0;
  height: 100%;
  width: 300px;
  background: var(--color-bg);
  color: var(--color-text);
  transform: translateX(100%);
  transition: transform 0.2s ease;
  z-index: 9999;
  display: flex;
  flex-direction: column;
}
.drawer.open {
  transform: translateX(0);
  box-shadow: 0 0 15px var(--color-primary);
}
.drawer-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid var(--color-border);
  background: var(--color-bg);
}
.drawer-title {
  font-weight: 600;
  color: var(--color-primary);
  font-size: var(--font-size-title);
}
.drawer-close {
  border: none;
  font-size: 18px;
  cursor: pointer;
  color: var(--color-text);
}
.drawer-close:hover {
  color: #f44336;
}
.drawer-content {
  display: flex;
  flex-direction: column;
  padding: 10px;
}
.drawer-item {
  border: none;
  padding: 12px;
  text-align: left;
  cursor: pointer;
  border-radius: 6px;
  transition: background 0.15s;
  font-size: var(--font-size-base);
  background: var(--color-bg);
  color: var(--color-text);
}
.drawer-item:hover {
  background: var(--color-primary-light);
  color: var(--color-primary);
}
.drawer-item.logout {
  color: #f44336;
}
.drawer-item.logout:hover {
  background: var(--color-danger-bg);
}


.modal-title{
  margin-bottom:12px;
  font-size: var(--font-size-title);
}
.modal-invites > .modal-window {
  height: 90% !important;
}

.invites-empty {
  padding: 12px;
  text-align: center;
  color: var(--color-text-muted);
  font-size: var(--font-size-title);
  font-style: italic;
}

.invites-list {
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

/* INVITES TRANSITION GROUP */
.anchor {
  width: 100%;
  height: 0;
  padding: 0;
  margin: 0;
  border: 0;
  overflow: hidden;
}
.invite-enter-from {
  opacity: 0;
}
.invite-enter-active {
  transition: all 0.3s ease;
}
.invite-enter-to {
  opacity: 1;
}

/* Анимация удаления инвайта */
.invite-leave-active {
  transition: all 0.3s;
}

.invite-leave-from {
  opacity: 1;
  transform: scale(1);
}

.invite-leave-to {
  opacity: 0;
  transform: scale(0.5);
}

/* Поднятие оставшихся инвайтов */
.invite-move {
  transition: transform 0.3s ease;
}


.invite-actions {
  display: flex;
  flex-direction: row;
  justify-content: space-evenly;
  gap: 8px;
  margin-top: 10px;
}
.inv-btn {
  border-radius: 50%;
  border: 1px solid;
  color: var(--color-text);
}
.accept {
  background: var(--color-success-bg);
  border-color: #4caf50;
}
.accept:hover {
  background: #4caf50;
}
.decline {
  background: var(--color-danger-bg);
  border-color: #f44336;
}
.decline:hover {
  background: #f44336;
}
</style>
