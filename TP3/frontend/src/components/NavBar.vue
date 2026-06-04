<template>
  <nav class="navbar">
    <span class="navbar-brand">✦ LifeTracker ✦</span>
    <div class="navbar-links">
      <RouterLink to="/dashboard">Inicio</RouterLink>
      <RouterLink to="/entries">Registros</RouterLink>
      <RouterLink to="/entries/new">+ Agregar</RouterLink>
      <RouterLink to="/summary/monthly">Mensual</RouterLink>
      <RouterLink to="/summary/annual">Anual</RouterLink>
      <button class="btn btn-danger" style="font-size:0.75rem; padding:0.35rem 0.8rem;" @click="auth.logout()">Salir</button>
    </div>
  </nav>
</template>

<script setup>
import { useAuthStore } from '@/stores/auth'
const auth = useAuthStore()
</script>

<style scoped>
.navbar {
  background: var(--color-surface);
  border-bottom: 1px solid var(--color-border);
  padding: 0.75rem 2rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: sticky;
  top: 0;
  z-index: 100;
}
.navbar-brand {
  font-family: var(--font-display);
  color: var(--color-gold);
  font-size: 1.1rem;
  letter-spacing: 0.15em;
}
.navbar-links { display: flex; align-items: center; gap: 1.5rem; }
.navbar-links a { font-family: var(--font-display); font-size: 0.8rem; letter-spacing: 0.06em; color: var(--color-muted); transition: color 0.2s; }
.navbar-links a:hover, .navbar-links a.router-link-active { color: var(--color-gold); }
</style>
