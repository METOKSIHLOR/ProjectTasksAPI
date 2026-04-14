<script setup>
import { useRouter } from 'vue-router'
import BaseForm from '../components/BaseForm.vue'
import { getCurrentUser, loginUser } from '../api/api.js'
import { setCurrentUser } from "../store/auth_store.js"
import {alertSuccess, alertError, clearAlerts, parseApiError} from '../store/alert_store.js'
import Alert from "../components/Alert.vue";

const router = useRouter()

const loginFields = [
  {
    name: 'email',
    label: 'Email',
    type: 'email',
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

async function submitLogin(formData) {
  try {
    const { email, password } = formData
    await loginUser(email, password)
    const user = await getCurrentUser()
    setCurrentUser(user)
    clearAlerts()
    alertSuccess('Login successful', `Welcome back ${user.name}`)
    await router.push('/')
  }
  catch (err) {
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
          submitText="Sign in"
          @submit="submitLogin"
      />

      <p class="auth-link">
        No account? <router-link to="/register">Register</router-link>
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
  gap: 16px;
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