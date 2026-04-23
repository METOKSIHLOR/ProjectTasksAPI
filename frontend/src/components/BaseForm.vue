<script setup>
import { reactive, ref, onMounted, watch, nextTick } from 'vue'
import BaseButton from './BaseButton.vue'
import * as yup from 'yup'

const props = defineProps({
  fields: {
    type: Array,
    required: true
  },
  submitText: {
    type: String,
    default: 'Submit'
  },
  schema: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['submit', 'setFocus'])

const form = reactive({})
const errors = reactive({})
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

// Инициализация формы
function initForm() {
  props.fields.forEach(field => {
    form[field.name] = field.value ?? ''
    errors[field.name] = ''
  })
}
function resetForm() {
  props.fields.forEach(field => {
    form[field.name] = field.value ?? ''
    errors[field.name] = ''
  })
}
function setFirstInput(el, index) {
  if (index === 0) firstInput.value = el
}
function setFocus() {
  console.log('onFocus')
  firstInput.value?.focus()
}
initForm()
watch(
    () => props.fields,
    () => initForm(),
    { deep: true }
)

// Очистка ошибок при изменении значений полей
watch(
    () => form,
    () => {
      // Очистка ошибок при изменении значения
      for (let fieldName in form) {
        if (errors[fieldName]) {
          errors[fieldName] = ''
        }
      }
    },
    { deep: true }
)

// Обработчик валидации
async function validate() {
  try {
    await props.schema.validate(form, { abortEarly: false }) // Все ошибки за один раз
    return true
  } catch (err) {
    // Ошибки сохраняются в объекте errors
    err.inner.forEach(e => {
      errors[e.path] = e.message
    })
    return false
  }
}

// Отправка формы
async function submitForm() {
  const isValid = await validate()
  if (!isValid) return

  let resolveSubmit
  const submitPromise = new Promise(resolve => {
    resolveSubmit = resolve
  })

  emit('submit', {
    data: { ...form },
    onSuccess: () => resolveSubmit(true),
    onError: () => resolveSubmit(false)
  })

  const success = await submitPromise

  if (success) {
    resetForm()
    await nextTick()
    firstInput.value?.focus()
  }
}

// ✅ универсальный Enter handler
function handleTextareaKeydown(e) {
  if (e.key !== 'Enter') return

  if (e.shiftKey) return // перенос строки

  e.preventDefault()
  submitForm()
}

onMounted(async () => {
  await nextTick()
  firstInput.value?.focus()
})
defineExpose({
  setFocus
})
</script>

<template>
  <form class="base-form" @submit.prevent="submitForm">
    <slot/>
    <div
        v-for="(field, index) in fields"
        :key="field.name"
        class="form-group"
    >
      <!-- LABEL -->
      <label v-if="field.label" class="form-label">
        <span>{{ field.label }}</span>
        <span v-if="errors[field.name]" class="form-error">{{ errors[field.name] }}</span>
      </label>

      <!-- INPUT (email, password, text, number, etc.) -->
      <input
          class="form-control"
          v-if="!field.type || textTypes.includes(field.type)"
          v-model="form[field.name]"
          :name="field.name"
          :id="field.name"
          :type="field.type || 'text'"
          :placeholder="field.placeholder"
          :disabled="field.disabled"
          :ref="el => setFirstInput(el,index)"
          autocomplete="off"
          :class="{'input-invalid': errors[field.name]}"
      />

      <!-- TEXTAREA -->
      <textarea
          class="form-control"
          v-else-if="field.type === 'textarea'"
          v-model="form[field.name]"
          :name="field.name"
          :id="field.name"
          :placeholder="field.placeholder"
          :disabled="field.disabled"
          :ref="el => setFirstInput(el,index)"
          :class="{'input-invalid': errors[field.name]}"
          @keydown="handleTextareaKeydown"
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
  gap: 10px;
  width: 100%;
}
.form-control {
  flex-grow: 1;
  width: 100%;
  padding: 10px 12px;
  border-radius: 6px;
  border: 1px solid var(--color-border);
  font: inherit;
  outline-color: var(--color-primary);
  background: var(--color-bg);
  color: var(--color-text);
}
.form-control:focus {
  outline-style: solid;
  outline-width: 2px;
}
.form-group {
  display: flex;
  flex-direction: column;
  flex-grow: 1;
  gap: 4px;
}

.form-label {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: baseline;
  font-size: var(--font-size-base);
  color: var(--color-text-muted);
}

textarea {
  resize: none;
  min-height: 80px;
}

.input-invalid {
  outline-color: red;
  background-color: var(--color-danger-bg);
}

.form-error {
  color: red;
  font-size: 12px;
}

select.form-control:hover {
  cursor: pointer;
}

select.form-control {
  appearance: none;
  -webkit-appearance: none;
  -moz-appearance: none;

  /* стрелка */
  background-image:
      linear-gradient(45deg, transparent 50%, var(--color-primary) 50%),
      linear-gradient(135deg, var(--color-primary) 50%, transparent 50%);
  background-position:
      calc(100% - 18px) calc(50% - 2px),
      calc(100% - 13px) calc(50% - 2px);
  background-size: 5px 5px, 5px 5px;
  background-repeat: no-repeat;
}

option {
  padding: 8px 10px;
  background: var(--color-bg);
  color: var(--color-text);
}
</style>