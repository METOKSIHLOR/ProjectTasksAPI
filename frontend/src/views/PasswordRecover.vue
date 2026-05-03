<script setup>

import Alert from "../components/Alert.vue";
import BaseForm from "../components/BaseForm.vue";
import router from "../router/index.js";
import {alertError, alertSuccess, parseApiError} from "../store/alert_store.js";
import * as yup from "yup";

const recoverForm = [
  {
    name: 'email',
    label: 'Assigned Email',
    type: 'email',
    placeholder: 'Enter email',
    value: ''
  },
  {
    name: 'new',
    label: 'New password',
    type: 'password',
    placeholder: 'Create new password',
    value: ''
  }
]
const recoverSchema = yup.object({
  email: yup.string().email('Invalid email format').required('Email is required'),
  new: yup.string().min(5, 'Password must be at least 6 characters').required('Password is required')
})

async function submitRecover({ data, onSuccess, onError }) {
  try {
    onSuccess()
    alertSuccess('Password changed', `(no)`)
    await router.push('/login')
  }
  catch (err) {
    onError()
    const { title, message } = parseApiError(err)
    alertError(title, message)
  }
}
</script>

<template>
  <div class="auth-page">
    <div class="auth-form">
      <h1>Recover password</h1>

      <BaseForm
          :fields="recoverForm"
          :schema="recoverSchema"
          submitText="Confirm"
          @submit="submitRecover"
      />

      <span class="auth-link">
        <span>Remember your password? <router-link to="/login">Back</router-link></span>
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
}

.auth-link a:hover {
  text-decoration: underline;
}
</style>