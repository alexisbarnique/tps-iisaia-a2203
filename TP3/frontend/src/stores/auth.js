import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/api/client'
import router from '@/router'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token'))

  const isAuthenticated = computed(() => !!token.value)

  async function login(email, password) {
    const res = await api.post('/auth/login', { email, password })
    token.value = res.data.access_token
    localStorage.setItem('token', token.value)
    await router.push('/dashboard')
  }

  async function register(email, password) {
    await api.post('/auth/register', { email, password })
    await login(email, password)
  }

  function logout() {
    token.value = null
    localStorage.removeItem('token')
    router.push('/login')
  }

  return { token, isAuthenticated, login, register, logout }
})
