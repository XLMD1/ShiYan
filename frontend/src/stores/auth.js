import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../api'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const isAuthenticated = ref(!!localStorage.getItem('access_token'))
  const initialized = ref(false)

  async function init() {
    if (initialized.value) return
    initialized.value = true
    const token = localStorage.getItem('access_token')
    if (token) {
      try {
        const { data } = await api.get('/auth/me/')
        user.value = data
        isAuthenticated.value = true
      } catch {
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
      }
    }
  }

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

  return { user, isAuthenticated, initialized, init, register, login, fetchUser, logout }
})
