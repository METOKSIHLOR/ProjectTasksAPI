<script setup>
import {useRouter} from 'vue-router'
import BaseForm from '../components/BaseForm.vue'
import {getCurrentUser, loginUser} from '../api/api.js'
import {setCurrentUser} from "../store/auth_store.js"
import {alertError, alertSuccess, clearAlerts, parseApiError} from '../store/alert_store.js'
import Alert from "../components/Alert.vue";
import * as yup from 'yup'
const router = useRouter()


const loginFields = [
  {
    name: 'email',
    label: 'Email',
    type: 'text',
    placeholder: 'Enter email',
    value: ''
  },
  {
    name: 'password',
    label: 'Password',
    type: 'password',
    placeholder: 'Enter password',
    value: ''
  }
]
// Схема валидации
const loginSchema = yup.object({
  email: yup.string().email('Invalid email format').required('Email is required'),
  password: yup.string().min(5, 'Password must be at least 6 characters').required('Password is required')
})

async function submitLogin({ data, onSuccess, onError }) {
  try {
    const { email, password } = data
    await loginUser(email, password)
    onSuccess()
    const user = await getCurrentUser()

    setCurrentUser(user)

    clearAlerts()
    alertSuccess('Login successful', `Welcome back ${user.name}`)
    await router.push('/')
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
      <h1>Sign in</h1>

      <BaseForm
          :fields="loginFields"
          :schema="loginSchema"
          submitText="Sign in"
          @submit="submitLogin"
      />

      <span class="auth-link">
        <span>No account? <router-link to="/register">Register</router-link></span>
        <router-link to="/password-recover">↺ recover password</router-link>
      </span>
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
  display: flex;
  flex-direction: row;
  justify-content: space-between;
}

.auth-link a {
  color: var(--color-primary);
  text-decoration: none;
  cursor: pointer;
}

.auth-link a:hover {
  text-decoration: underline;
}
</style>