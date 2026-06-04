<template>
  <div class="card entry-card">
    <div class="entry-header">
      <span class="category-icon">{{ icon }}</span>
      <strong>{{ entry.title }}</strong>
      <span class="entry-date">{{ formatDate(entry.date) }}</span>
    </div>
    <div class="entry-meta">
      <span v-if="entry.saga_name">📖 {{ entry.saga_name }} #{{ entry.saga_part }}</span>
      <span v-if="entry.season_number">Temporada {{ entry.season_number }}</span>
      <span v-if="entry.country">{{ entry.city ? `${entry.city}, ` : '' }}{{ entry.country }}</span>
      <span v-if="entry.place_type">{{ entry.place_type }}</span>
      <span v-if="entry.rating">{{ '★'.repeat(entry.rating) }}{{ '☆'.repeat(5 - entry.rating) }}</span>
    </div>
    <p v-if="entry.notes" class="entry-notes">{{ entry.notes }}</p>
    <div class="entry-actions">
      <RouterLink :to="`/entries/${entry.id}/edit`" class="btn" style="font-size:0.75rem; padding:0.3rem 0.7rem">Editar</RouterLink>
      <button class="btn btn-danger" style="font-size:0.75rem; padding:0.3rem 0.7rem" @click="$emit('delete', entry.id)">Eliminar</button>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({ entry: Object })
defineEmits(['delete'])

const icons = { event: '🎵', movie_series: '🎬', book: '📚', city: '🗺️', place: '🏛️' }
const icon = icons[props.entry.category] || '•'

function formatDate(d) {
  return new Date(d + 'T00:00:00').toLocaleDateString('es-AR', { day: '2-digit', month: 'long', year: 'numeric' })
}
</script>

<style scoped>
.entry-card { margin-bottom: 1rem; }
.entry-header { display: flex; align-items: baseline; gap: 0.6rem; margin-bottom: 0.4rem; }
.entry-date { margin-left: auto; font-size: 0.85rem; color: var(--color-muted); }
.entry-meta { display: flex; flex-wrap: wrap; gap: 0.75rem; font-size: 0.88rem; color: var(--color-muted); margin-bottom: 0.4rem; }
.entry-notes { font-style: italic; color: var(--color-muted); font-size: 0.9rem; margin-bottom: 0.75rem; }
.entry-actions { display: flex; gap: 0.5rem; }
</style>
