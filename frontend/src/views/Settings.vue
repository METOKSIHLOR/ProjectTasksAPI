<script setup>
import {computed, onBeforeUnmount, onMounted, ref, toRaw} from 'vue';
import { currentUser, updateUserSettings } from '../store/auth_store.js'; // Подключаем необходимые функции
import DashboardLayout from '../components/Layout.vue';
import BaseCard from '../components/BaseCard.vue';
import BaseButton from "../components/BaseButton.vue";
import router from "../router/index.js";
import {alertError, alertInfo, alertSuccess, parseApiError} from "../store/alert_store.js";
import {saveUserSettings} from "../api/api.js";

const settings = [
  {
    label: 'Font size',
    key: 'fontSize',
    options: ['normal', 'large'],
  },
  {
    label: 'Layout width',
    key: 'layoutWidth',
    options: ['normal', 'wide'],
  },
  {
    label: 'Theme color',
    key: 'primaryHue',
    options: ['red', 'orange', 'yellow', 'green', 'sky', 'blue', 'purple'],
  },
  {
    label: 'Theme',
    key: 'theme',
    options: ['light', 'dark'],
  }
]

const userSettings = computed(() => currentUser.value ? currentUser.value.settings : {})

const originalSettings = ref(
    JSON.parse(JSON.stringify(currentUser.value.settings))
)
const isSettingsChanged = computed(() => {
  if (!currentUser.value) return false

  return JSON.stringify(currentUser.value.settings) !== JSON.stringify(originalSettings.value)
})

function updateSetting(key, value) {
  if (currentUser.value) {
    updateUserSettings({ ...currentUser.value.settings, [key]: value });
  }
}

async function saveChanges() {
  try {
    const settingsToSave = {
      settings: toRaw(currentUser.value.settings)
    };
    await saveUserSettings(settingsToSave);
    alertInfo('Done', 'Settings saved');
    originalSettings.value = JSON.parse(
        JSON.stringify(currentUser.value.settings)
    )
  }
  catch (err) {
    const { title, message } = parseApiError(err);
    alertError(title, message);
  }
}

// Уходим со страницы
function goBack() {
  if (window.history.length > 1) {
    router.back();
  } else {
    router.push('/');
  }
}

// Обновляем настройки, когда уходим со страницы
onBeforeUnmount(() => {
  if (isSettingsChanged.value) {
    saveChanges();
  }
});
import { connectWS } from '../api/ws'

onMounted(() => {

})
</script>

<template>
  <DashboardLayout>
    <template #title>
      <span class="settings-title">Settings</span>
    </template>

    <template #header>
      <BaseButton @click="goBack">⮜ Back</BaseButton>
    </template>

    <div class="settings-list">
      <BaseCard>
        <template #nickname>
          <h2 class="list-header">GUI Settings</h2>
          <BaseButton v-if="isSettingsChanged" class="save-btn" @click="saveChanges">🖫</BaseButton>
        </template>
        <div class="settings-line"></div>

        <div v-for="setting in settings" :key="setting.key" class="setting-block">
          <span class="setting-label">{{ setting.label }}</span>
          <div class="radio-group">
            <label
                v-for="opt in setting.options"
                :key="opt"
                class="radio-pill"
                :class="{ active: userSettings[setting.key] === opt }"
            >
              <input
                  type="radio"
                  v-model="userSettings[setting.key]"
                  :value="opt"
                  @change="updateSetting(setting.key, opt)"
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
.list-header {
  margin: 7px 0;
}
.settings-line {
  margin-top: 6px;
  border-top: 1px solid var(--color-primary) !important;
}
.settings-title {
  font-size: var(--font-size-title);
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