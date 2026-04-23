<script setup>
import { useRouter } from 'vue-router'
import BaseForm from '../components/BaseForm.vue'
import { registerUser } from '../api/api.js'
import Alert from "../components/Alert.vue";
import {alertError, alertSuccess, parseApiError} from "../store/alert_store.js";
import * as yup from 'yup'
const router = useRouter()

const registerFields = [
  {
    name: 'name',
    label: 'Name',
    placeholder: 'Enter your name',
    type: 'text',
    value: ''
  },
  {
    name: 'email',
    label: 'Email',
    placeholder: 'Enter your email',
    type: 'text',
    value: ''
  },
  {
    name: 'password',
    label: 'Password',
    placeholder: 'Enter your password',
    type: 'password',
    value: ''
  }
]

// Схема валидации для регистрации
const registerSchema = yup.object({
  email: yup
      .string()
      .email('Invalid email format') // Проверка на корректный формат почты
      .required('Email is required'),  // Почта обязательна

  password: yup
      .string()
      .min(5, 'Password must be at least 5 characters') // Пароль должен быть не менее 5 символов
      .required('Password is required'),  // Пароль обязательный

  name: yup
      .string()
      .min(3, 'Name must be at least 3 characters') // Имя не менее 3 символов
      .required('Name is required')  // Имя обязательно
})

async function submitRegister({ data, onSuccess, onError }) {
  try {
    await registerUser(data.name, data.email, data.password)
    onSuccess()
    await router.push('/login')
    alertSuccess(
        '[200] success',
        `
        Account registered:
        name: ${data.name}
        email: ${data.email}
        `
    )
  }
  catch (err) {
    onError()
    const { title, message } = parseApiError(err)
    alertError(title, message)
  }
}
</script>

<template>
  <Alert/>
  <div class="auth-page">
    <div class="auth-form">
      <h1>Create account</h1>

      <BaseForm
          :fields="registerFields"
          submitText="Create account"
          @submit="submitRegister"
          :schema="registerSchema"
      />

      <p class="auth-link">
        Already have an account?
        <router-link to="/login">Login</router-link>
      </p>
    </div>
  </div>
</template>

<style scoped>
.auth-page {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
}

.auth-form {
  width: 320px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.auth-link {
  text-align: center;
  font-size: 14px;
}

.auth-link a {
  color: var(--color-primary);
  text-decoration: none;
}

.auth-link a:hover {
  text-decoration: underline;
}
</style>