<template>
  <div>
    <h1 class="page-title">✦ Tu año en resumen ✦</h1>
    <div class="picker card" style="max-width:200px; margin-bottom:1.5rem">
      <div class="form-group">
        <label>Año</label>
        <input v-model.number="year" type="number" :min="2020" :max="currentYear" />
      </div>
      <button class="btn btn-primary" style="width:100%" @click="load">Ver año</button>
    </div>

    <div v-if="loading" class="muted-text">Cargando…</div>
    <div v-else-if="loaded && summary.months.length === 0" class="muted-text">Sin registros en {{ year }}.</div>

    <template v-else-if="loaded">
      <div class="totals-banner card" style="margin-bottom:2rem">
        <h2>{{ year }} — totales</h2>
        <div class="totals-grid">
          <div v-for="(count, cat) in displayTotals" :key="cat" class="total-item">
            <span class="total-icon">{{ catIcon(cat) }}</span>
            <span class="total-count">{{ count }}</span>
            <span class="total-label">{{ catLabel(cat) }}</span>
          </div>
        </div>
      </div>

      <div v-for="block in summary.months" :key="block.month" class="month-section">
        <h3 class="month-heading">{{ monthName(block.month) }}</h3>
        <SummaryBlock v-for="h in block.highlights" :key="h.category" :highlight="h" />
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import api from '@/api/client'
import SummaryBlock from '@/components/SummaryBlock.vue'

const today = new Date()
const currentYear = today.getFullYear()
const year = ref(currentYear)
const summary = ref({ months: [], totals: {} })
const loading = ref(false)
const loaded = ref(false)

const icons = { event: '🎵', movie_series: '🎬', book: '📚', city: '🗺️', place: '🏛️', city_countries: '🌍' }
const labels = { event: 'eventos', movie_series: 'películas/series', book: 'libros', city: 'ciudades', place: 'lugares', city_countries: 'países' }

const displayTotals = computed(() => {
  const t = summary.value.totals
  return Object.fromEntries(Object.entries(t).filter(([, v]) => v > 0))
})

function catIcon(cat) { return icons[cat] || '•' }
function catLabel(cat) { return labels[cat] || cat }
function monthName(m) { return new Date(2000, m - 1, 1).toLocaleDateString('es-AR', { month: 'long' }) }

async function load() {
  loading.value = true
  loaded.value = false
  try {
    const res = await api.get(`/summaries/annual/${year.value}`)
    summary.value = res.data
    loaded.value = true
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.muted-text { color: var(--color-muted); font-style: italic; text-align: center; padding: 2rem; }
.totals-grid { display: flex; flex-wrap: wrap; gap: 1.5rem; margin-top: 1rem; }
.total-item { display: flex; flex-direction: column; align-items: center; gap: 0.2rem; }
.total-icon { font-size: 1.5rem; }
.total-count { font-family: var(--font-display); font-size: 2rem; color: var(--color-gold); }
.total-label { font-size: 0.8rem; color: var(--color-muted); }
.month-section { margin-bottom: 2rem; }
.month-heading { font-family: var(--font-display); color: var(--color-gold); font-size: 1rem; text-transform: capitalize; margin-bottom: 0.75rem; padding-bottom: 0.3rem; border-bottom: 1px solid var(--color-border); }
</style>
