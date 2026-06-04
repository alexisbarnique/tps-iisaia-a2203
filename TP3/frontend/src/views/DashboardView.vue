<template>
  <div>
    <h1 class="page-title">✦ Tu mundo este mes ✦</h1>
    <p class="period-label">{{ monthName }} {{ currentYear }}</p>

    <div v-if="loading" class="muted-text">Cargando…</div>
    <div v-else-if="highlights.length === 0" class="muted-text empty-state">
      <p>Aún no hay registros este mes.</p>
      <RouterLink to="/entries/new" class="btn btn-primary" style="margin-top:1rem">Agregar el primero</RouterLink>
    </div>
    <div v-else>
      <SummaryBlock v-for="h in highlights" :key="h.category" :highlight="h" />
    </div>

    <div class="quick-links">
      <RouterLink to="/entries/new" class="btn btn-primary">+ Agregar registro</RouterLink>
      <RouterLink to="/summary/monthly" class="btn">Ver historial mensual</RouterLink>
      <RouterLink to="/summary/annual" class="btn">Ver año completo</RouterLink>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/api/client'
import SummaryBlock from '@/components/SummaryBlock.vue'

const today = new Date()
const currentYear = today.getFullYear()
const currentMonth = today.getMonth() + 1
const monthName = today.toLocaleDateString('es-AR', { month: 'long' })

const highlights = ref([])
const loading = ref(false)

onMounted(async () => {
  loading.value = true
  try {
    const res = await api.get(`/summaries/monthly/${currentYear}/${currentMonth}`)
    highlights.value = res.data.highlights
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.period-label { color: var(--color-muted); font-style: italic; margin-bottom: 1.5rem; text-transform: capitalize; }
.muted-text { color: var(--color-muted); font-style: italic; text-align: center; padding: 2rem; }
.empty-state { display: flex; flex-direction: column; align-items: center; }
.quick-links { display: flex; gap: 1rem; margin-top: 2rem; flex-wrap: wrap; }
</style>
