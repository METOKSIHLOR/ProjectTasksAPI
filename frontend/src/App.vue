<script setup>
import { RouterView } from 'vue-router'
import { getCurrentUser } from './api/api.js'
import { setCurrentUser } from './store/auth_store.js'
import Alert from "./components/Alert.vue";

async function loadUser(){
  try{
    const user = await getCurrentUser()
    setCurrentUser(user)
  }catch(e){
    console.error('Failed to load current user', e)
  }
}


</script>

<template>
  <Alert/>
  <RouterView />
</template>

<style>
</style>