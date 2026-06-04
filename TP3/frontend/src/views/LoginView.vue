<template>
  <div class="login-page">
    <div class="login-card card">
      <h1>✦ LifeTracker ✦</h1>
      <p class="subtitle">Guardián de tus memorias</p>

      <div class="tab-row">
        <button :class="['tab', { active: mode === 'login' }]" @click="mode = 'login'">Ingresar</button>
        <button :class="['tab', { active: mode === 'register' }]" @click="mode = 'register'">Registrarse</button>
      </div>

      <form @submit.prevent="submit">
        <div class="form-group">
          <label>Correo electrónico</label>
          <input v-model="email" type="email" required placeholder="tu@email.com" />
        </div>
        <div class="form-group">
          <label>Contraseña</label>
          <input v-model="password" type="password" required placeholder="••••••••" />
        </div>
        <p v-if="error" class="error-msg">{{ error }}</p>
        <button type="submit" class="btn btn-primary" style="width:100%">
          {{ mode === 'login' ? 'Ingresar' : 'Crear cuenta' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const mode = ref('login')
const email = ref('')
const password = ref('')
const error = ref('')

async function submit() {
  error.value = ''
  try {
    if (mode.value === 'login') {
      await auth.login(email.value, password.value)
    } else {
      await auth.register(email.value, password.value)
    }
  } catch (e) {
    error.value = e.response?.data?.detail || 'Error al procesar la solicitud'
  }
}
</script>

<style scoped>
.login-page {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  padding: 2rem;
}
.login-card {
  width: 100%;
  max-width: 400px;
  padding: 2rem;
  text-align: center;
}
.login-card h1 { margin-bottom: 0.25rem; }
.subtitle { color: var(--color-muted); font-style: italic; margin-bottom: 1.5rem; }
.tab-row { display: flex; gap: 0; margin-bottom: 1.5rem; border: 1px solid var(--color-border); border-radius: var(--radius); overflow: hidden; }
.tab { flex: 1; padding: 0.5rem; background: transparent; border: none; color: var(--color-muted); font-family: var(--font-display); font-size: 0.8rem; cursor: pointer; transition: all 0.2s; }
.tab.active { background: var(--color-gold); color: var(--color-bg); }
form { text-align: left; }
</style>
