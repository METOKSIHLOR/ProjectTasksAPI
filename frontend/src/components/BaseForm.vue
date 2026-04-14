<script setup>
import {reactive, ref, onMounted, watch, nextTick} from 'vue'
import BaseButton from './BaseButton.vue'

const props = defineProps({
  fields: {
    type: Array,
    required: true
  },
  submitText: {
    type: String,
    default: 'Submit'
  }
})

const emit = defineEmits(['submit'])

const form = reactive({})
const firstInput = ref(null)

const textTypes = [
  'text',
  'email',
  'password',
  'number',
  'tel',
  'url',
  'search'
]

/**
 * инициализация/ресет формы
 */
function initForm() {
  props.fields.forEach(field => {
    form[field.name] = field.value ?? ''
  })
}

initForm()

watch(
    () => props.fields,
    () => initForm(),
    { deep: true }
)

function setFirstInput(el, index) {
  if (index === 0) firstInput.value = el
}

function submitForm() {
  emit('submit', { ...form })
}

onMounted(async () => {
  await nextTick()
  firstInput.value?.focus()
})
</script>

<template>
  <form class="base-form" @submit.prevent="submitForm">

    <div
        v-for="(field, index) in fields"
        :key="field.name"
        class="form-group"
    >
      <!-- LABEL -->
      <label v-if="field.label" class="form-label">
        {{ field.label }}
      </label>

      <!-- INPUT (email, password, text, number, etc.) -->
      <input class="form-control"
          v-if="!field.type || textTypes.includes(field.type)"
          v-model="form[field.name]"
          :name="field.name"
          :id="field.name"
          :type="field.type || 'text'"
          :placeholder="field.placeholder"
          :disabled="field.disabled"
          :ref="el => setFirstInput(el,index)"
          autocomplete="off"
      />

      <!-- TEXTAREA -->
      <textarea class="form-control"
          v-else-if="field.type === 'textarea'"
          v-model="form[field.name]"
          :name="field.name"
          :id="field.name"
          :placeholder="field.placeholder"
          :disabled="field.disabled"
          :ref="el => setFirstInput(el,index)"
      />

      <!-- SELECT -->
      <select class="form-control"
          v-else-if="field.type === 'select'"
          v-model="form[field.name]"
          :name="field.name"
          :id="field.name"
          :disabled="field.disabled"
          :ref="el => setFirstInput(el,index)"
      >
        <option disabled value="">Select task performer</option>
        <option
            v-for="opt in field.options"
            :key="opt.value"
            :value="opt.value"
        >
          {{ opt.label }}
        </option>
      </select>

    </div>

    <BaseButton type="submit">
      {{ submitText }}
    </BaseButton>

  </form>
</template>

<style scoped>
.base-form {
  display: flex;
  flex-direction: column;
  gap: 14px;
  width: 100%;
}
.form-control {
  width: 100%;
  padding: 10px 12px;
  border-radius: 6px;
  border: 1px solid var(--color-primary-light);
  font: inherit;
  outline-color: var(--color-primary);
  background: var(--color-card);
  color: var(--color-text);
}
.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-label {
  font-size: var(--font-size-base);
  color: var(--color-text);
}

textarea {
  resize: none;
  min-height: 80px;
}
</style>