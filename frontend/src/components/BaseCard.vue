<script setup>
import BaseButton from './BaseButton.vue'

const props = defineProps({
  type: { type: String, default: 'default' },
  clickable: { type: Boolean, default: false },
  deletable: { type: Boolean, default: false }
})

const emit = defineEmits(['click','delete', 'reply'])

const handleClick = () => props.clickable && emit('click')

const handleDelete = (e) => {
  e.stopPropagation()
  emit('delete')
}
const createReply = (e) => {
  e.stopPropagation()
  emit('reply')
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
      <div v-if="$slots.reply" class="reply-slot">
        <slot name="reply" />
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
    <BaseButton
        class="reply-btn"
        @click="createReply"
    >
      ⮌
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
  border: 1px solid var(--color-border);
  max-width: 100%;
  transition: all 0.2s ease;
}
.base-card.clickable {
  cursor: pointer;
}
.base-card.clickable:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 10px var(--color-primary);
}

.card-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  font-size: var(--font-size-base);
}
.nickname-slot {
  display: flex;
  justify-content: space-between;
  align-items: center;

  font-size: var(--font-size-base);
  color: var(--color-primary);
  font-weight: 500;
}

/* delete button */
.delete-btn {
  display: none;
  position: absolute;
  align-items: center;
  justify-content: center;

  margin: 0;
  padding: 0;
  top: -9px;
  right: -9px;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  font-size: 12px !important;
  background: var(--color-bg);
  border: 1px solid var(--color-border);
  color: #f44336;
}
.base-card:hover .delete-btn {
  display: flex;
}
.base-card.comment-owner .delete-btn {
  top: -6px;
  right: -6px;
  width: 24px;
  height: 24px;
  font-size: var(--font-size-base);
}
.delete-btn:hover {
  background: #f44336;
  border-color: #f44336;
  color: #ffffff;
}


/* ======== КОММЕНТАРИИ ======== */
.reply-btn {
  position: absolute;
  display: none;
  justify-content: center;
  align-items: center;

  padding: 0;
  bottom: 0;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  font-size: 12px !important;
  border: 1px solid var(--color-border);
  background: var(--color-bg);
  color: var(--color-text);
}

.reply-slot {
  display: flex;
  flex-direction: column;

  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;

  margin: 2px 0;
  padding: 2px 6px;
  font-size: 12px;
  line-height: normal;
  border-radius: 5px;
  border-left: 5px solid var(--color-primary);
  background: var(--color-reply-bg);
  color: #333333;
}
.reply-slot:has(.deleted) {
  border-color: orangered;
}

.base-card.comment-owner,
.base-card.comment-companion {
  max-width: 70%;
  padding: 10px 10px;
  line-height: normal;
  font-size: var(--font-size-base);
  display: inline-block;
  position: relative;
  word-break: break-word;
  border-radius: 20px;
  box-shadow: none;
  min-width: calc(var(--font-size-base) + 28px);
}
.reply-btn:hover {
  background-color: var(--color-primary);
  color: white;
}
.base-card.comment-owner:hover .reply-btn,
.base-card.comment-companion:hover .reply-btn {
  display: flex;
}
.base-card.status:hover .reply-btn {
  display: flex;
  bottom: 0;
  right: -12px;
}

/* Свой комментарий */
.base-card.comment-owner {
  align-self: flex-end;
  background: var(--color-comment-bg);
  color: var(--color-text);
  border: 1px solid var(--color-comment-bg);
  margin-left: auto;
  margin-right: 12px;
  border-bottom-right-radius: 0 !important;
}
.base-card.comment-owner::after {
  position: absolute;
  content: '';
  bottom: -1px;
  right: -12px;
  width: 12px;
  height: 12px;
  background: var(--color-comment-bg);
  clip-path: polygon(0 0, 100% 100%, 0 100%);
  transition: 0.2s ease;
}
.base-card.comment-owner:hover .reply-btn {
  left: -22px !important;
}


/* Чужой комментарий */
.base-card.comment-companion {
  align-self: flex-start;
  background: transparent;
  color: var(--color-text);
  border: 1px solid var(--color-primary);
  margin-right: auto;
  margin-left: 12px;
  border-bottom-left-radius: 0 !important;
}
.base-card.comment-companion::before {
  content: "";
  position: absolute;
  bottom: -1px;
  left: -12px;
  width: 12px;
  height: 12px;
  background: var(--color-primary);
  clip-path: polygon(0 100%, 100% 0, 100% 100%);
  transition: 0.2s ease;
}
.base-card.comment-companion:hover .reply-btn {
  right: -22px !important;
}


/* Наведение на удаление */
.base-card:has(.delete-btn:hover) {
  border-color: #f44336;
  background-color: var(--color-danger-bg);
}
.base-card.comment-owner:has(.delete-btn:hover) {
  color: var(--color-text);
  border: 1px solid var(#f44336);
}
.base-card.comment-owner:has(.delete-btn:hover)::after {
  background-color: #f44336;
}


/* ======== СТАТУСЫ ======== */
.base-card.status {
  align-self: center;
  width: auto;
  border: none;
  background: transparent;
  font-style: italic;
  font-size: var(--font-size-base);
  padding: 0 24px;
  box-shadow: none;
}
</style>