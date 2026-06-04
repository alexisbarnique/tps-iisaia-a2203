<template>
  <div>
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1.5rem">
      <h1 class="page-title" style="margin-bottom:0">Mis registros</h1>
      <RouterLink to="/entries/new" class="btn btn-primary">+ Agregar</RouterLink>
    </div>

    <div class="filter-row">
      <select v-model="filterCategory" @change="load">
        <option value="">Todas las categorías</option>
        <option value="event">🎵 Eventos</option>
        <option value="movie_series">🎬 Películas/Series</option>
        <option value="book">📚 Libros</option>
        <option value="city">🗺️ Ciudades</option>
        <option value="place">🏛️ Lugares</option>
      </select>
    </div>

    <div v-if="loading" class="muted-text">Cargando…</div>
    <div v-else-if="entries.length === 0" class="muted-text">No hay registros todavía.</div>
    <EntryCard
      v-for="entry in entries"
      :key="entry.id"
      :entry="entry"
      @delete="handleDelete"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useEntriesStore } from '@/stores/entries'
import EntryCard from '@/components/EntryCard.vue'

const store = useEntriesStore()
const entries = ref([])
const filterCategory = ref('')
const loading = ref(false)

async function load() {
  loading.value = true
  const filters = filterCategory.value ? { category: filterCategory.value } : {}
  entries.value = await store.fetchEntries(filters)
  loading.value = false
}

async function handleDelete(id) {
  if (!confirm('¿Eliminar este registro?')) return
  await store.deleteEntry(id)
  entries.value = entries.value.filter(e => e.id !== id)
}

onMounted(load)
</script>

<style scoped>
.filter-row { margin-bottom: 1.5rem; }
.filter-row select { background: var(--color-surface); border: 1px solid var(--color-border); color: var(--color-text); font-family: var(--font-body); padding: 0.4rem 0.75rem; border-radius: var(--radius); }
.muted-text { color: var(--color-muted); font-style: italic; text-align: center; padding: 2rem; }
</style>
