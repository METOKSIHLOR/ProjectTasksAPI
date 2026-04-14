<script setup>
import { useRouter } from 'vue-router'
import BaseButton from './BaseButton.vue'
import ModalWindow from './ModalWindow.vue'
import { logoutUser, updateCurrentUserName } from '../api/api.js'
import { currentUser, clearCurrentUser } from '../store/auth_store.js'
import {
  ref,
  computed,
  nextTick,
  watch,
  onMounted,
  onUnmounted,
  defineExpose
} from 'vue'
import Alert from "./Alert.vue";
import {alertError, alertSuccess, parseApiError} from "../store/alert_store.js";

/* router & refs */
const router = useRouter()
const mainContainer = ref(null)

/* drawer menu state */
const menuOpen = ref(false)
const openMenu = () => menuOpen.value = true
const closeMenu = () => menuOpen.value = false

/* change name modal state */
const showChangeName = ref(false)
const currentNameInput = ref('')
const newNameInput = ref('')
const currentNameField = ref(null)
const newNameField = ref(null)

/* change name validation */
const currentNameValid = computed(() => {
  return currentNameInput.value.trim() === currentUser.value?.name
})

/* change name actions */
async function submitNameChange() {
  if (!currentNameValid.value || !newNameInput.value.trim()) return

  const newName = newNameInput.value.trim()

  try {
    await updateCurrentUserName(newName)
    currentUser.value.name = newName
    resetNameForm()
    showChangeName.value = false
    alertSuccess(
        'Success',
        `Name changed. Hello, ${newName}`
    )
  }
  catch (err) {
    const { title, message } = parseApiError(err)
    alertError(title, message)
  }
}

function resetNameForm() {
  currentNameInput.value = ''
  newNameInput.value = ''
}

/* logout */
async function handleLogout() {
  try {
    await logoutUser()
    clearCurrentUser()
    menuOpen.value = false
    await router.push('/login')
  }
  catch (err) {
    const { title, message } = parseApiError(err)
    alertError(title, message)
  }
}

/* scroll helpers */
async function scrollToBottomInstant() {
  await nextTick()
  if (mainContainer.value) {
    mainContainer.value.scrollTop = mainContainer.value.scrollHeight
  }
}

async function scrollToBottomSmooth() {
  await nextTick()
  if (mainContainer.value) {
    mainContainer.value.scrollTo({
      top: mainContainer.value.scrollHeight,
      behavior: 'smooth'
    })
  }
}

/* modal autofocus watchers */
watch(showChangeName, async (val) => {
  if (val) {
    await nextTick()
    currentNameField.value?.focus()
  } else {
    resetNameForm()
  }
})
watch(currentNameValid, async (val) => {
  if (val) {
    await nextTick()
    newNameField.value?.focus()
  }
})

/* keyboard events */
function handleKeydown(e) {
  if (e.key === 'Escape' && menuOpen.value) {
    closeMenu()
  }
}

/* lifecycle events */
onMounted(() => {
  window.addEventListener('keydown', handleKeydown)
})
onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown)
})

/* exposed layout methods */
defineExpose({
  scrollToBottomInstant,
  scrollToBottomSmooth
})
</script>

<template>
  <div class="dashboard-layout">

    <header class="header">
      <div class="header-left">
        <div class="logo">
          <div class="logo-icon">T</div>
          <slot name="title"/>
        </div>
      </div>

      <div class="header-right">
        <slot name="header"/>
        <BaseButton v-if="currentUser" @click="openMenu">☰</BaseButton>
      </div>
    </header>

    <Alert />

    <div v-if="menuOpen" class="drawer-overlay" @click="closeMenu"></div>

    <div class="drawer" :class="{open:menuOpen}">
      <div class="drawer-header">
        <span class="drawer-title">{{currentUser?.name}}</span>
        <button class="drawer-close" @click="closeMenu">✕</button>
      </div>

      <div class="drawer-content">
        <button class="drawer-item" @click="showChangeName=true;closeMenu()">
          ✎ Change Name
        </button>

        <button class="drawer-item">
          ✎ {{currentUser?.email}}
        </button>

        <button class="drawer-item">
          ✎ Change Password
        </button>

        <button class="drawer-item">
          ↺ Recover Password
        </button>

        <button class="drawer-item" @click="router.push('/settings');closeMenu()">
          ⛭ Settings
        </button>

        <button class="drawer-item logout" @click="handleLogout">
          🠈 Log Out
        </button>
      </div>
    </div>

    <div class="content-top">
      <div class="content-inner-top">
        <slot name="content-top"/>
      </div>
    </div>

    <main class="main" ref="mainContainer">
      <div class="scroll-fade-top"></div>

      <div class="content-inner-main">
        <slot/>
      </div>

      <div class="scroll-fade-bottom"></div>
    </main>

    <div class="content-bottom">
      <div class="content-inner-bottom">
        <slot name="content-bottom"/>
      </div>
    </div>

    <footer class="footer">
      <span class="footer-label">Frontend by</span>
      <span class="frontend-name">ImmortalTrap</span>
      <span class="footer-separator">•</span>
      <span class="footer-label">Backend by</span>
      <span class="backend-name">METOKS</span>
    </footer>

    <ModalWindow v-if="showChangeName" @close="showChangeName=false">
      <div class="change-name-form">
        <h3 class="modal-title">Change your name</h3>

        <input
            class="name-input"
            ref="currentNameField"
            v-model="currentNameInput"
            placeholder="Current name"
            :readonly="currentNameValid"
            :class="{ valid: currentNameValid }"
        />

        <input
            class="name-input"
            ref="newNameField"
            v-model="newNameInput"
            placeholder="New name"
            :disabled="!currentNameValid"
        />

        <BaseButton
            :disabled="!currentNameValid || !newNameInput"
            @click="submitNameChange"
        >
          Save
        </BaseButton>
      </div>
    </ModalWindow>

  </div>
</template>

<style scoped>

/* layout structure */
.dashboard-layout{
  height:100vh;
  display:flex;
  flex-direction:column;
}

/* header */
.header{
  display:flex;
  align-items:center;
  justify-content:space-between;
  padding:0 24px;
  height:60px;
  border-bottom:1px solid #e5e5e5;
  flex-shrink:0;
}

.header-left{
  display:flex;
  align-items:center;
  gap:10px;
}

.header-right{
  display:flex;
  align-items:center;
  gap:10px;
}

.logo{
  display:flex;
  align-items:center;
  gap:10px;
  font-weight:600;
  font-size:var(--font-size-base);
}

.logo-icon{
  width:32px;
  height:32px;
  border-radius:50%;
  background:var(--color-primary);
  color:white;
  display:flex;
  align-items:center;
  justify-content:center;
  font-weight:700;
}

/* drawer menu */
.drawer-overlay{
  position:fixed;
  inset:0;
  background:rgba(0,0,0,0.25);
  backdrop-filter: blur(2px);
  z-index:10;
}

.drawer{
  position:fixed;
  top:0;
  right:0;
  height:100%;
  width:260px;
  background: var(--color-bg);
  color: var(--color-text);
  box-shadow:-4px 0 12px rgba(0,0,0,0.1);
  transform:translateX(100%);
  transition:transform .25s ease;
  z-index:11;
  display:flex;
  flex-direction:column;
}

.drawer.open{
  transform:translateX(0);
}

.drawer-header{
  display:flex;
  justify-content:space-between;
  align-items:center;
  padding:16px;
  border-bottom:1px solid var(--color-primary);
  background: var(--color-primary-light);
}

.drawer-title{
  font-weight:600;
  color: var(--color-primary);
  font-size: var(--font-size-title);
}

.drawer-close{
  border:none;
  font-size:18px;
  cursor:pointer;
}

.drawer-close:hover{
  color:#f44336;
}

.drawer-content{
  display:flex;
  flex-direction:column;
  padding:10px;
}

.drawer-item{
  border:none;
  padding:12px;
  text-align:left;
  cursor:pointer;
  border-radius:6px;
  transition:background .15s;
  font-size: var(--font-size-base);
  background: var(--color-bg);
  color: var(--color-text);
}

.drawer-item:hover{
  background:var(--color-primary-light);
  color: var(--color-primary);
}

.drawer-item.logout{
  color:#f44336;
}

.drawer-item.logout:hover{
  background:#ffebee;
}
.name-input {
  outline-color: var(--color-primary);
  background: var(--color-card);
  color: var(--color-text);
}
.modal-title{
  margin-bottom:10px;
  font-size: var(--font-size-title);
}
/* content areas */
.content-top,
.content-bottom{
  flex-shrink:0;
}

.content-inner-top{
  max-width:var(--layout-width);
  width:100%;
  margin:12px auto;
  padding:0 20px;
  transition: max-width 0.3s ease;
}

.main{
  flex:1;
  overflow-y:auto;
  position:relative;
}

.content-inner-main{
  max-width:var(--layout-width);
  transition: max-width 0.3s ease;
  width:100%;
  margin:0 auto;
  padding:16px 20px;
  display:flex;
  flex-direction:column;
  gap:10px;
}

.content-inner-bottom{
  max-width:var(--layout-width);
  transition: max-width 0.3s ease;
  width:100%;
  margin:0 auto;
  padding:6px 20px 10px 20px;
  display:flex;
  flex-direction:column;
  gap:8px;
}

/* modal form */
.change-name-form{
  display:flex;
  flex-direction:column;
  gap:10px;
}

.change-name-form input{
  padding:8px 10px;
  border:1px solid #ccc;
  border-radius:6px;
  transition:all 0.15s;
}

.change-name-form input:disabled{
  background:#f5f5f5;
  color:#999;
  border-color:#ddd;
  cursor:not-allowed;
}

.change-name-form input.valid{
  background:#e8f5e9;
  border-color:#66bb6a;
  color:#2e7d32;
}

.change-name-form input.valid{
  cursor:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='24' height='24'><text x='4' y='18' font-size='18'>✓</text></svg>") 12 12, pointer;
}

/* scroll effects */
.scroll-fade-bottom{
  position:sticky;
  bottom:0;
  left:0;
  right:0;
  height:40px;
  pointer-events:none;
  background: linear-gradient(
      to bottom,
      transparent,
      var(--color-bg)
  );
}

/* footer */
.footer{
  height:60px;
  display:flex;
  align-items:center;
  justify-content:center;
  gap:6px;
  padding:0 24px;
  border-top:1px solid #e5e5e5;
  font-size:calc(var(--font-size-base) - 2px);
  flex-shrink:0;
}

.footer-label{
  color:#777;
}

.frontend-name,
.backend-name{
  font-weight:600;
  color:var(--color-primary);
}

.footer-separator{
  margin:0 6px;
  color:#ccc;
}
</style>