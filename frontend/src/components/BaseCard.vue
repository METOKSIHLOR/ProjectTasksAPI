<script setup>
import BaseButton from './BaseButton.vue'

const props = defineProps({
  type: { type: String, default: 'default' },
  clickable: { type: Boolean, default: false },
  deletable: { type: Boolean, default: false }
})

const emit = defineEmits(['click','delete'])

const handleClick = () => props.clickable && emit('click')

const handleDelete = (e) => {
  e.stopPropagation()
  emit('delete')
}
</script>

<template>
  <div
      class="base-card"
      :class="[type, { clickable }]"
      @click="handleClick"
  >
    <div class="card-content">
      <div v-if="$slots.nickname" class="nickname-slot">
        <slot name="nickname" />
      </div>
      <slot />
    </div>
    <BaseButton
        v-if="deletable"
        class="delete-btn"
        @click="handleDelete"
    >
      ✕
    </BaseButton>
  </div>
</template>

<style scoped>
.base-card {
  position: relative;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-radius: 12px;
  background: var(--color-bg);
  border: 1px solid #e6e6e6;
  transition: transform 0.15s, box-shadow 0.15s, border-color 0.15s;
  max-width: 100%;
  box-sizing: border-box;
}
.base-card.clickable {
  cursor: pointer;
}
.base-card.clickable:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 12px rgba(0,0,0,0.08);
}

.card-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  font-size: var(--font-size-base);
}
.nickname-slot {
  font-size: var(--font-size-base);
  color: var(--color-primary);
  font-weight: 500;
  margin-bottom: 2px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
}

/* delete button */
.delete-btn {
  position: absolute;
  top: -10px;
  right: -10px;
  width: 30px;
  height: 30px;
  padding: 0;
  align-items: center;
  justify-content: center;
  text-align: center;
  border-radius: 50%;
  font-size: 12px !important;
  line-height: 1;
  background: var(--color-bg);
  border: 1px solid #e6e6e6;
  color: #f44336;
  display: none;
  transition: all 0.15s;
}
.base-card.comment-owner .delete-btn {
  top: -6px;
  right: -6px;
  width: 20px;
  height: 20px;
  font-size: var(--font-size-base);
}
.base-card:hover .delete-btn {
  display: flex;
}
.delete-btn:hover {
  background: #f44336;
  border-color: #f44336;
  color: #ffffff;
}

.base-card:has(.delete-btn:hover) {
  border-color: #f44336;
  background-color: #ffebee;
  color: #333;
  transition: 0.2s ease;
}
.base-card.comment-owner:has(.delete-btn:hover) {
  background-color: #ffebee;
}
.base-card.comment-owner:has(.delete-btn:hover)::after {
  background-color: #ffebee;
}

/* === Комментарии === */
.base-card.comment-owner,
.base-card.comment-companion {
  max-width: 70%;
  padding: 8px 12px;
  font-size: var(--font-size-base);
  line-height: 1.4;
  display: inline-block;
  position: relative;
  word-break: break-word;
  box-sizing: border-box;
  border-radius: 12px;
  box-shadow: none;
  border: none;
}

/* Свой комментарий */
.base-card.comment-owner {
  align-self: flex-end;
  background: var(--color-primary-light);
  color: #333;
  margin-left: auto;
  border-bottom-right-radius: 0 !important;
}
.base-card.comment-owner::after {
  content: "";
  position: absolute;
  bottom: 0;
  right: -12px;
  width: 12px;
  height: 12px;
  background: var(--color-primary-light);
  clip-path: polygon(0 0, 100% 100%, 0 100%);
}

/* Чужой комментарий */
.base-card.comment-companion {
  align-self: flex-start;
  background: none;
  color: var(--color-text);
  border: 1px solid var(--color-primary) !important;
  margin-right: auto;
  border-bottom-left-radius: 0 !important;
}
.base-card.comment-companion::after {
  content: "";
  position: absolute;
  bottom: -1px;
  left: -12px;
  width: 12px;
  height: 12px;
  background: var(--color-primary);
  clip-path: polygon(0 100%, 100% 0, 100% 100%);
}

/* status message */
.base-card.status {
  align-self: center;
  width: auto;
  border: none;
  background: transparent;
  font-style: italic;
  font-size: var(--font-size-base);
  padding: 6px 10px;
  box-shadow: none;
}
</style>