import { ref } from 'vue'

export const currentUser = ref(null) // null = неизвестно, false = не авторизован, объект = авторизован

export function setCurrentUser(user) {
    currentUser.value = user
}

export function setUnauthorized() {
    currentUser.value = false
}

export function clearCurrentUser() {
    currentUser.value = null
}