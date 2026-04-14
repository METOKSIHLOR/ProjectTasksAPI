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
            :deletable="alert.type === 'error'"
            @delete="removeAlert(alert.id)"
        >
          <template #nickname>
            <span :class="`title title-${alert.type}`">{{ alert.title }}</span>
          </template>

          <div v-if="alert.text" class="alert-text">
            {{ alert.text }}
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
  top: 70px;
  right: 20px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  z-index: 9999;
  max-width: 240px;
}
.alert {
  border-radius: 10px;
  margin-top: 6px;
}
.alert-text {
  margin-top: 4px;
  font-size: 16px;
  opacity: 0.9;
}

/* INFO */
.alert-info {
  border: 1px solid #2196f3;
  background: #e3f2fd;
  color: #0d47a1;
}

/* SUCCESS */
.alert-success {
  border: 1px solid #4caf50;
  background: #e8f5e9;
  color: #1b5e20;
}

/* ERROR */
.alert-error {
  border: 1px solid #f44336;
  background: #ffebee;
  color: #b71c1c;
}


.title {
  font-weight: bold;
  font-size: 20px;
}
.title-info {
  color: #0d47a1;
}
.title-success {
  color: #1b5e20;
}
.title-error {
  color: #b71c1c;
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