<template>
  <div>
    <h1 class="page-title">Resumen mensual</h1>
    <div class="picker card" style="max-width:300px; margin-bottom:1.5rem">
      <div class="form-group">
        <label>Año</label>
        <input v-model.number="year" type="number" :min="2020" :max="currentYear" />
      </div>
      <div class="form-group">
        <label>Mes</label>
        <select v-model.number="month">
          <option v-for="m in 12" :key="m" :value="m">{{ monthName(m) }}</option>
        </select>
      </div>
      <button class="btn btn-primary" style="width:100%" @click="load">Ver resumen</button>
    </div>

    <div v-if="loading" class="muted-text">Cargando…</div>
    <div v-else-if="loaded && highlights.length === 0" class="muted-text">Sin registros en este período.</div>
    <template v-else-if="loaded">
      <h2 style="margin-bottom:1rem; text-transform:capitalize">{{ monthName(month) }} {{ year }}</h2>
      <SummaryBlock v-for="h in highlights" :key="h.category" :highlight="h" />
    </template>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import api from '@/api/client'
import SummaryBlock from '@/components/SummaryBlock.vue'

const today = new Date()
const currentYear = today.getFullYear()
const year = ref(currentYear)
const month = ref(today.getMonth() + 1)
const highlights = ref([])
const loading = ref(false)
const loaded = ref(false)

function monthName(m) {
  return new Date(2000, m - 1, 1).toLocaleDateString('es-AR', { month: 'long' })
}

async function load() {
  loading.value = true
  loaded.value = false
  try {
    const res = await api.get(`/summaries/monthly/${year.value}/${month.value}`)
    highlights.value = res.data.highlights
    loaded.value = true
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.muted-text { color: var(--color-muted); font-style: italic; text-align: center; padding: 2rem; }
</style>
