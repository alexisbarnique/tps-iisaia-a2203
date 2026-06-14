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

    <div v-if="yearGoals.length > 0" class="goals-widget">
      <div class="goals-widget-label">🎯 Metas {{ currentYear }}</div>
      <div class="goals-chips">
        <div v-for="g in yearGoals" :key="g.id" class="goal-chip">
          <svg viewBox="0 0 36 36" class="chip-svg">
            <circle cx="18" cy="18" r="15.9" fill="none" stroke="var(--color-border)" stroke-width="4"/>
            <circle
              cx="18" cy="18" r="15.9" fill="none"
              :stroke="g.percentage >= 100 ? '#27c97a' : 'var(--color-gold)'"
              stroke-width="4"
              :stroke-dasharray="`${Math.min(g.percentage, 100)} ${Math.max(100 - g.percentage, 0)}`"
              stroke-linecap="round"
            />
          </svg>
          <span :class="{ 'chip-done': g.percentage >= 100 }">
            {{ icons[g.category] }} {{ g.current }}/{{ g.target }}
          </span>
        </div>
      </div>
      <RouterLink to="/goals" class="see-goals">Ver todas las metas →</RouterLink>
    </div>

    <div class="quick-links">
      <RouterLink to="/entries/new" class="btn btn-primary">+ Agregar registro</RouterLink>
      <RouterLink to="/summary/monthly" class="btn">Ver historial mensual</RouterLink>
      <RouterLink to="/summary/annual" class="btn">Ver año completo</RouterLink>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '@/api/client'
import { useGoalsStore } from '@/stores/goals'
import SummaryBlock from '@/components/SummaryBlock.vue'

const today = new Date()
const currentYear = today.getFullYear()
const currentMonth = today.getMonth() + 1
const monthName = today.toLocaleDateString('es-AR', { month: 'long' })

const highlights = ref([])
const loading = ref(false)
const goalsStore = useGoalsStore()
const icons = { event: '🎵', movie_series: '🎬', book: '📚', city: '🗺️', place: '🏛️' }

const yearGoals = computed(() => goalsStore.goals.filter(g => g.year === currentYear))

onMounted(async () => {
  loading.value = true
  try {
    const [summaryRes] = await Promise.all([
      api.get(`/summaries/monthly/${currentYear}/${currentMonth}`),
      goalsStore.fetchGoals(),
    ])
    highlights.value = summaryRes.data.highlights
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

.goals-widget {
  margin-top: 1.5rem;
  padding: 1rem 1.25rem;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
}
.goals-widget-label {
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--color-muted);
  margin-bottom: 0.75rem;
}
.goals-chips { display: flex; flex-wrap: wrap; gap: 0.75rem; margin-bottom: 0.75rem; }
.goal-chip {
  display: flex; align-items: center; gap: 0.45rem;
  font-size: 0.82rem; color: var(--color-text);
}
.chip-svg { width: 32px; height: 32px; transform: rotate(-90deg); flex-shrink: 0; }
.chip-done { color: #27c97a; }
.see-goals { font-size: 0.78rem; color: var(--color-muted); }
.see-goals:hover { color: var(--color-gold); }
</style>
