<script setup>
import DashboardLayout from '../components/Layout.vue'
import BaseCard from '../components/BaseCard.vue'
import BaseButton from "../components/BaseButton.vue"

import router from "../router/index.js"
import { styles, getStyleOptions } from '../store/style_store.js'

function goBack() {
  if (window.history.length > 1) {
    router.back()
  } else {
    router.push('/')
  }
}
</script>

<template>
  <DashboardLayout>

    <!-- TITLE -->
    <template #title>
      <span class="settings-title">Settings</span>
    </template>

    <!-- HEADER -->
    <template #header>
      <BaseButton @click="goBack">🠈 Back</BaseButton>
    </template>

    <!-- CONTENT -->
    <div class="settings-list">

      <BaseCard>
        <template #nickname>
          GUI Settings
        </template>

        <!-- FONT SIZE -->
        <div class="setting-block">
          <span class="setting-label">Font size</span>

          <div class="radio-group">
            <label
                v-for="opt in getStyleOptions('fontSize')"
                :key="opt"
                class="radio-pill"
                :class="{ active: styles.fontSize === opt }"
            >
              <input
                  type="radio"
                  v-model="styles.fontSize"
                  :value="opt"
              />
              {{ opt }}
            </label>
          </div>
        </div>

        <!-- LAYOUT WIDTH -->
        <div class="setting-block">
          <span class="setting-label">Layout width</span>

          <div class="radio-group">
            <label
                v-for="opt in getStyleOptions('layoutWidth')"
                :key="opt"
                class="radio-pill"
                :class="{ active: styles.layoutWidth === opt }"
            >
              <input
                  type="radio"
                  v-model="styles.layoutWidth"
                  :value="opt"
              />
              {{ opt }}
            </label>
          </div>
        </div>

        <!-- THEME COLOR -->
        <div class="setting-block">
          <span class="setting-label">Theme color</span>

          <div class="radio-group">
            <label
                v-for="opt in getStyleOptions('primaryHue')"
                :key="opt"
                class="radio-pill"
                :class="{ active: styles.primaryHue === opt }"
            >
              <input
                  type="radio"
                  v-model="styles.primaryHue"
                  :value="opt"
              />
              {{ opt }}
            </label>
          </div>
        </div>

        <!-- DARK / LIGHT -->
        <div class="setting-block">
          <span class="setting-label">Theme</span>

          <div class="radio-group">
            <label
                v-for="opt in getStyleOptions('theme')"
                :key="opt"
                class="radio-pill"
                :class="{ active: styles.theme === opt }"
            >
              <input
                  type="radio"
                  v-model="styles.theme"
                  :value="opt"
              />
              {{ opt }}
            </label>
          </div>
        </div>

      </BaseCard>

    </div>

  </DashboardLayout>
</template>

<style scoped>
.settings-title {
  font-size: calc(var(--font-size-base) + 4px);
}

.settings-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

/* блок настройки */
.setting-block {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 10px 0;
}

.setting-label {
  font-weight: 500;
  color: var(--color-text);
}

/* группа radio */
.radio-group {
  display: flex;
  gap: 8px;
}

/* pill button */
.radio-pill {
  display: flex;
  align-items: center;
  gap: 6px;

  padding: 4px 10px;
  border-radius: 999px;

  border: 1px solid var(--color-primary);
  color: var(--color-primary);
  cursor: pointer;

  font-size: calc(var(--font-size-base) - 1px);

  transition: 0.15s;
}

/* скрываем input */
.radio-pill input {
  display: none;
}

/* hover */
.radio-pill:hover {
  background: var(--color-primary);
  color: white;
}

/* active state */
.radio-pill.active {
  background: var(--color-primary);
  color: white;
}
</style>