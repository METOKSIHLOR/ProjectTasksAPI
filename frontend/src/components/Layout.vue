<script setup>
import BaseButton from './BaseButton.vue'
import {currentUser} from '../store/auth_store.js'
import {ref, nextTick, onMounted, onUnmounted, defineExpose } from 'vue'
import Alert from "./Alert.vue";
import Sidebar from "./Sidebar.vue";
import {useRoute} from "vue-router";

/* refs */
const route = useRoute()
const mainContainer = ref(null)
const isMainExpanded = ref(true)  // Стейт для переключения блоков

/* переключатель растяжения */
function toggleStretch() {
  isMainExpanded.value = !isMainExpanded.value
  nextTick()
}


/* sidebar menu state */
const menuOpen = ref(false)
const openMenu = () => menuOpen.value = true
const closeMenu = () => menuOpen.value = false


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

/* keyboard events */
function handleKeydown(e) {
  if (e.key === 'Escape' && menuOpen.value) {
    closeMenu()
  }
}

const atBottom = ref(false)
const atTop = ref(false)
function handleScroll() {
  const el = mainContainer.value
  if (!el) return
  const threshold = 4 // защита от дробных пикселей
  atTop.value = el.scrollTop <= threshold
  atBottom.value = el.scrollTop + el.clientHeight >= el.scrollHeight - threshold
}


/* lifecycle events */
onMounted(() => {
  window.addEventListener('keydown', handleKeydown)

  window.addEventListener('keydown', handleKeydown)
  mainContainer.value?.addEventListener('scroll', handleScroll)
  handleScroll()
})
onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown)

  window.removeEventListener('keydown', handleKeydown)
  mainContainer.value?.removeEventListener('scroll', handleScroll)
})

/* exposed layout methods */
defineExpose({
  toggleStretch,
  scrollToBottomInstant,
  scrollToBottomSmooth
})
</script>

<template>
  <div class="dashboard-layout">

    <header class="header">
      <div class="header-left">
        <div class="logo">
          <div class="logo-icon">
            <svg viewBox="0 0 32 32" class="logo-svg">
              <circle cx="16" cy="16" r="16" />
              <path
                  d="M8 10 H24 V13 H18 V24 H14 V13 H8 Z"
                  class="logo-letter"
              />
            </svg>
          </div>
          <slot name="title"/>
        </div>
      </div>

      <div v-if="route.name === 'task'" class="header-center">
        <slot name="header-center"/>
      </div>

      <div class="header-right">
        <slot name="header"/>
        <BaseButton v-if="currentUser" @click="openMenu">☰</BaseButton>
      </div>
    </header>

    <Alert />

    <Sidebar :menuOpen="menuOpen" :closeMenu="closeMenu"/>

    <div class="content-top">
      <div class="content-inner-top">
        <slot name="content-top"/>
      </div>
    </div>

    <main :class="{'stretch': isMainExpanded}" class="main" ref="mainContainer">
      <div class="content-inner-main">
        <div class="scroll-fade-top" :class="{ hidden: atTop }"></div>
        <slot/>
        <div class="scroll-fade-bottom" :class="{ hidden: atBottom }"></div>
      </div>
    </main>

    <div class="content-top">
      <div class="content-inner-top">
        <slot name="members-header"/>
      </div>
    </div>

    <div :class="{'stretch': !isMainExpanded}" class="content-bottom">
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

  </div>
</template>

<style scoped>
.stretch {
  flex: 1 !important;
}

/* layout structure */
.dashboard-layout{
  height:100dvh;
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
  border-bottom:1px solid var(--color-border);
  flex-shrink:0;
}
.header-left{
  display:flex;
  justify-content: start;
  flex: 1;
  align-items:center;
  gap:10px;
}
.header-center {
  display: flex;
  justify-content: center;
  flex: 1;
  padding: 6px 0;
  height: 100%;
}
.header-right{
  display:flex;
  justify-content: end;
  flex: 1;
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
.logo-icon {
  width: 46px;
  height: 46px;
}
.logo-svg {
  width: 100%;
  height: 100%;
  display: block;
}
.logo-svg circle {
  fill: var(--color-primary);
}
.logo-letter {
  fill: #ffffff;
}
/* content areas */
.content-top,
.content-bottom{
  flex-shrink:0;
  transition: all 0.3s ease;
}

.content-inner-top{
  max-width:var(--layout-width);
  width:100%;
  margin:12px auto;
  padding:0 20px;
  transition: max-width 0.3s ease;
}

.main{
  overflow-y:auto;
  scrollbar-gutter: stable both-edges;
  overscroll-behavior: contain;
  position:relative;
  transition: all 0.3s ease;
}

.content-bottom{
  overflow-y:auto;
  scrollbar-gutter: stable both-edges;
  overscroll-behavior: contain;
  position:relative;
  transition: all 0.3s ease;
}

.content-inner-main{
  max-width:var(--layout-width);
  transition: max-width 0.3s ease;
  width:100%;
  margin:0 auto;
  padding:10px 20px;
  display:flex;
  flex-direction:column;
}

.content-inner-bottom{
  max-width:var(--layout-width);
  transition: max-width 0.3s ease;
  width:100%;
  margin:0 auto;
  padding:10px 20px;
  display:flex;
  flex-direction:column;
  gap:10px;
}

/* scroll effects */
.scroll-fade-top,
.scroll-fade-bottom{
  z-index:2;
}
.scroll-fade-top{
  position:sticky;
  top:0;
  height:50px;
  margin-bottom:-50px;
  pointer-events:none;
  background:linear-gradient(to top, transparent, var(--color-bg));
  transition:all .2s ease;
}

.scroll-fade-top.hidden{
  height:0;
  opacity:0;
  margin-bottom: 0;
}

.scroll-fade-bottom{
  position:sticky;
  bottom:0;
  height:50px;
  margin-top:-50px;
  pointer-events:none;
  background:linear-gradient(to bottom, transparent, var(--color-bg));
  transition:all .25s ease;
}

.scroll-fade-bottom.hidden{
  height:0;
  opacity:0;
  margin-top: 0;
}

/* footer */
.footer{
  height:60px;
  display:flex;
  align-items:center;
  justify-content:center;
  gap:6px;
  padding:0 24px;
  border-top:1px solid var(--color-border);
  font-size:calc(var(--font-size-base) - 2px);
  flex-shrink:0;
}

.footer-label{
  color:var(--color-text-muted);
}

.frontend-name,
.backend-name{
  font-weight:600;
  color:var(--color-primary);
}

.footer-separator{
  margin:0 6px;
  color:var(--color-text-muted);
}


</style>