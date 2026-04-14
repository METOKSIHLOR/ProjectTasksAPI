<script setup>
import { onMounted, onUnmounted } from 'vue'

const emit = defineEmits(['close'])

function handleKey(e) {
  if (e.key === 'Escape') {
    emit('close')
  }
}

onMounted(() => {
  window.addEventListener('keydown', handleKey)
  document.body.style.overflow = 'hidden'
})
onUnmounted(() => {
  window.removeEventListener('keydown', handleKey)
  document.body.style.overflow = ''
})
</script>

<template>
  <div class="modal-overlay">
    <div class="modal-window">
      <button class="close-btn" @click="$emit('close')">✕</button>
      <slot />
    </div>
  </div>
</template>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0,0,0,0.2);
  backdrop-filter: blur(6px);
  z-index: 1000;
  animation: fadeIn 0.2s ease;
}

.modal-window {
  position: relative;
  width:calc(var(--layout-width) / 2) ;
  padding: 24px;
  background: var(--color-bg);
  color: var(--color-text);
  border-radius: 10px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.15);
  animation: scaleIn 0.2s ease;
}

.close-btn {
  position: absolute;
  top: 10px;
  right: 10px;
  color: var(--color-text);
  border: none;
  font-size: 18px;
  cursor: pointer;
}
.close-btn:hover {
  color: #f44336;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}
@keyframes scaleIn {
  from {
    transform: scale(0.95);
    opacity: 0;
  }
  to {
    transform: scale(1);
    opacity: 1;
  }
}

textarea {
  width: 100%;
  min-height: 120px;
  padding: 10px 12px;
  border-radius: 6px;
  border: 1px solid #ccc;
  font: inherit;
  resize: vertical;
}
</style>