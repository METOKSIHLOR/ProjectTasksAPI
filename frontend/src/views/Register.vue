<script setup>
import { useRouter } from 'vue-router'
import BaseForm from '../components/BaseForm.vue'
import { registerUser } from '../api/api.js'
import {alertError, alertSuccess, parseApiError} from "../store/alert_store.js";
import Alert from "../components/Alert.vue";

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
    type: 'email',
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

async function submitRegister(data) {
  try {
    const result = await registerUser(data.name, data.email, data.password)
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