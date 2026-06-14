<template>
  <div class="card goal-card">
    <div class="goal-main">
      <div class="goal-circle">
        <svg viewBox="0 0 36 36">
          <circle cx="18" cy="18" r="15.9" fill="none" stroke="var(--color-border)" stroke-width="3.5"/>
          <circle
            cx="18" cy="18" r="15.9" fill="none"
            :stroke="goal.percentage >= 100 ? '#27c97a' : 'var(--color-gold)'"
            stroke-width="3.5"
            :stroke-dasharray="`${Math.min(goal.percentage, 100)} ${Math.max(100 - goal.percentage, 0)}`"
            stroke-linecap="round"
          />
        </svg>
        <span class="goal-pct" :class="{ completed: goal.percentage >= 100 }">
          {{ Math.round(goal.percentage) }}%
        </span>
      </div>
      <div class="goal-info">
        <div class="goal-category">{{ icons[goal.category] }} {{ labels[goal.category] }}</div>
        <div class="goal-count">{{ goal.current }} / {{ goal.target }}</div>
        <div class="goal-year">Meta {{ goal.year }}</div>
      </div>
    </div>
    <div class="goal-actions">
      <RouterLink
        :to="`/goals/${goal.id}/edit`"
        class="btn"
        style="font-size:0.75rem;padding:0.3rem 0.7rem"
      >Editar</RouterLink>
      <button
        class="btn btn-danger"
        style="font-size:0.75rem;padding:0.3rem 0.7rem"
        @click="$emit('delete', goal.id)"
      >Eliminar</button>
    </div>
  </div>
</template>

<script setup>
defineProps({ goal: Object })
defineEmits(['delete'])

const icons = { event: '🎵', movie_series: '🎬', book: '📚', city: '🗺️', place: '🏛️' }
const labels = { event: 'Eventos', movie_series: 'Películas/Series', book: 'Libros', city: 'Ciudades', place: 'Lugares' }
</script>

<style scoped>
.goal-card { margin-bottom: 1rem; }
.goal-main { display: flex; align-items: center; gap: 1.25rem; margin-bottom: 0.75rem; }
.goal-circle { position: relative; width: 64px; height: 64px; flex-shrink: 0; }
.goal-circle svg { width: 64px; height: 64px; transform: rotate(-90deg); }
.goal-pct {
  position: absolute; inset: 0;
  display: flex; align-items: center; justify-content: center;
  font-size: 0.78rem; font-weight: 700; color: var(--color-text);
}
.goal-pct.completed { color: #27c97a; }
.goal-category { font-size: 0.8rem; color: var(--color-muted); margin-bottom: 0.2rem; }
.goal-count { font-size: 1.1rem; font-weight: 700; color: var(--color-text); }
.goal-year { font-size: 0.75rem; color: var(--color-muted); margin-top: 0.1rem; }
.goal-actions { display: flex; gap: 0.5rem; }
</style>
