<template>
  <div id="app">
    <NavBar v-if="auth.isAuthenticated" />
    <main class="main-content">
      <RouterView />
    </main>
  </div>
</template>

<script setup>
import { useAuthStore } from '@/stores/auth'
import NavBar from '@/components/NavBar.vue'
const auth = useAuthStore()
</script>
