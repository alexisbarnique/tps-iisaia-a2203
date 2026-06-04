<template>
  <div class="summary-block card">
    <div class="summary-header">
      <span class="category-icon">{{ icon }}</span>
      <span class="summary-title">{{ categoryLabel }}</span>
      <span class="summary-count">{{ highlight.count }}</span>
    </div>

    <div v-if="highlight.category === 'city'" class="summary-detail">
      <span>{{ highlight.countries }} {{ highlight.countries === 1 ? 'país' : 'países' }}, {{ highlight.cities }} {{ highlight.cities === 1 ? 'ciudad' : 'ciudades' }}</span>
      <div class="item-list">
        <span v-for="item in highlight.items" :key="item.city" class="item-chip">
          {{ item.city }}<span v-if="item.country">, {{ item.country }}</span>
        </span>
      </div>
    </div>

    <div v-else-if="highlight.category === 'place'" class="summary-detail">
      <div class="by-type">
        <span v-for="(count, type) in highlight.by_type" :key="type" class="item-chip">{{ count }} {{ type }}</span>
      </div>
    </div>

    <div v-else class="summary-detail">
      <div class="item-list">
        <span v-for="item in highlight.items" :key="item.title" class="item-chip">
          {{ item.title }}<span v-if="item.saga_name"> ({{ item.saga_name }})</span>
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({ highlight: Object })
const icons = { event: '🎵', movie_series: '🎬', book: '📚', city: '🗺️', place: '🏛️' }
const labels = { event: 'Eventos', movie_series: 'Películas y series', book: 'Libros', city: 'Ciudades', place: 'Lugares' }
const icon = icons[props.highlight.category] || '•'
const categoryLabel = labels[props.highlight.category] || props.highlight.category
</script>

<style scoped>
.summary-block { margin-bottom: 1rem; }
.summary-header { display: flex; align-items: center; gap: 0.6rem; margin-bottom: 0.75rem; }
.summary-title { font-family: var(--font-display); font-size: 0.9rem; color: var(--color-gold); }
.summary-count { margin-left: auto; font-family: var(--font-display); font-size: 1.4rem; color: var(--color-gold); }
.summary-detail { color: var(--color-muted); font-size: 0.9rem; }
.item-list, .by-type { display: flex; flex-wrap: wrap; gap: 0.4rem; margin-top: 0.4rem; }
.item-chip { background: var(--color-surface-raised); border: 1px solid var(--color-border); border-radius: 999px; padding: 0.2rem 0.7rem; font-size: 0.82rem; color: var(--color-text); }
</style>
