import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../api'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const isAuthenticated = ref(false)

  async function register(username, password, email) {
    const { data } = await api.post('/auth/register/', { username, password, email })
    return data
  }

  async function login(username, password) {
    const { data } = await api.post('/auth/login/', { username, password })
    localStorage.setItem('access_token', data.access)
    localStorage.setItem('refresh_token', data.refresh)
    isAuthenticated.value = true
    await fetchUser()
    return data
  }

  async function fetchUser() {
    try {
      const { data } = await api.get('/auth/me/')
      user.value = data
      isAuthenticated.value = true
    } catch {
      logout()
    }
  }

  function logout() {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    user.value = null
    isAuthenticated.value = false
  }

  return { user, isAuthenticated, register, login, fetchUser, logout }
})
