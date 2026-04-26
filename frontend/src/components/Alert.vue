<script setup>
import { alerts, removeAlert } from '../store/alert_store.js'
import BaseCard from "./BaseCard.vue";
</script>

<template>
  <div class="alert-container">
    <div style="position: relative;">
      <TransitionGroup name="alert">
        <div key="alert-anchor" class="alert-anchor"></div>

        <BaseCard
            v-for="alert in alerts"
            :key="alert.id"
            :class="`alert alert-${alert.type}`"
            :clickable="false"
            :deletable="false"
            @delete="removeAlert(alert.id)"
        >
          <template #nickname>
            <span :class="`title title-${alert.type}`">{{ alert.title }}</span>
          </template>

          <div v-if="alert.text" class="alert-text">
            {{ alert.text }}
          </div>

          <!-- progress bar -->
          <div class="alert-progress">
            <div
                class="alert-progress-bar"
                :style="{animationDuration: (alert.timeout || 3000) + 'ms'}"
            ></div>
          </div>

        </BaseCard>
      </TransitionGroup>
    </div>
  </div>
</template>

<style scoped>
.alert-anchor {
  width: 240px;
  height: 0;
  padding: 0;
  margin: 0;
  border: 0;
  overflow: hidden;
}

.alert-container {
  position: fixed;
  top: 147px;
  right: 20px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  z-index: 9998;
  max-width: 240px;
}

.alert {
  border-radius: 10px;
  margin-top: 6px;
  position: relative;
  overflow: hidden;
}

.alert-text {
  margin-top: 4px;
  font-size: var(--font-size-base);
  opacity: 0.9;
}

/* INFO */
.alert-info {
  border: 1px solid #2196f3;
  background: var(--color-info-bg);
  color: #2196f3;
}

/* SUCCESS */
.alert-success {
  border: 1px solid #4caf50;
  background: var(--color-success-bg);
  color: #4caf50;
}

/* ERROR */
.alert-error {
  border: 1px solid #f44336;
  background: var(--color-danger-bg);
  color: #b71c1c;
}

.title {
  font-weight: bold;
  font-size: var(--font-size-title);
}

.title-info {
  color: #2196f3;
}

.title-success {
  color: #4caf50;
}

.title-error {
  color: #b71c1c;
}

/* progress bar */
.alert-progress {
  position: absolute;
  left: 0;
  bottom: 0;
  width: 100%;
  height: 3px;
  background: transparent;
}
.alert-progress-bar {
  height: 100%;
  width: 100%;
  background: currentColor;
  transform-origin: left;
  animation-name: shrink;
  animation-timing-function: linear;
  animation-fill-mode: forwards;
}

@keyframes shrink {
  from {
    transform: scaleX(1);
  }
  to {
    transform: scaleX(0);
  }
}

/* появление */
.alert-enter-from {
  opacity: 0;
  transform: translateY(-8px);
}

.alert-enter-active {
  transition: all 0.25s ease;
}

.alert-enter-to {
  opacity: 1;
  transform: translateY(0);
}

/* исчезновение */
.alert-leave-active {
  position: absolute;
  transition: all 0.35s ease;
}

.alert-leave-from {
  opacity: 1;
  transform: translateX(0);
}

.alert-leave-to {
  opacity: 0;
  transform: translateX(120%);
}

/* движение карточек */
.alert-move {
  transition: transform 0.25s ease;
}
</style>