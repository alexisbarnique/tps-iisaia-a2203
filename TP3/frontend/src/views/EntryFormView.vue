<template>
  <div>
    <h1 class="page-title">{{ isEditing ? 'Editar registro' : 'Nuevo registro' }}</h1>
    <div class="card" style="max-width:600px">
      <form @submit.prevent="submit">
        <div class="form-group">
          <label>Categoría</label>
          <select v-model="form.category" required @change="resetCategoryFields">
            <option value="">— elegir —</option>
            <option value="event">🎵 Evento / Concierto</option>
            <option value="movie_series">🎬 Película / Serie</option>
            <option value="book">📚 Libro</option>
            <option value="city">🗺️ Ciudad</option>
            <option value="place">🏛️ Lugar (restaurante, museo…)</option>
          </select>
        </div>

        <div class="form-group">
          <label>{{ titleLabel }}</label>
          <input v-model="form.title" type="text" required :placeholder="titlePlaceholder" />
        </div>

        <div class="form-group">
          <label>Fecha</label>
          <input v-model="form.date" type="date" required />
        </div>

        <template v-if="form.category === 'movie_series'">
          <div class="form-group">
            <label>Saga (opcional)</label>
            <input v-model="form.saga_name" type="text" placeholder="ej: Harry Potter, MCU" />
          </div>
          <div v-if="form.saga_name" class="form-group">
            <label>Número de entrega en la saga</label>
            <input v-model.number="form.saga_part" type="number" min="1" />
          </div>
          <div class="form-group">
            <label>Temporada (solo series)</label>
            <input v-model.number="form.season_number" type="number" min="1" placeholder="ej: 4" />
          </div>
          <div class="form-group">
            <label>Calificación (1–5)</label>
            <input v-model.number="form.rating" type="number" min="1" max="5" />
          </div>
        </template>

        <template v-if="form.category === 'book'">
          <div class="form-group">
            <label>Saga (opcional)</label>
            <input v-model="form.saga_name" type="text" placeholder="ej: El señor de los anillos" />
          </div>
          <div v-if="form.saga_name" class="form-group">
            <label>Número de entrega en la saga</label>
            <input v-model.number="form.saga_part" type="number" min="1" />
          </div>
          <div class="form-group">
            <label>Calificación (1–5)</label>
            <input v-model.number="form.rating" type="number" min="1" max="5" />
          </div>
        </template>

        <template v-if="form.category === 'city'">
          <div class="form-group">
            <label>País</label>
            <input v-model="form.country" type="text" placeholder="ej: Francia" />
          </div>
        </template>

        <template v-if="form.category === 'place'">
          <div class="form-group">
            <label>Tipo de lugar</label>
            <select v-model="form.place_type" required>
              <option value="">— elegir —</option>
              <option value="restaurant">Restaurante</option>
              <option value="cafe">Café</option>
              <option value="museum">Museo</option>
              <option value="bar">Bar</option>
              <option value="park">Parque</option>
              <option value="other">Otro</option>
            </select>
          </div>
          <div class="form-group">
            <label>Ciudad (opcional)</label>
            <input v-model="form.city" type="text" placeholder="ej: París" />
          </div>
          <div class="form-group">
            <label>País (opcional)</label>
            <input v-model="form.country" type="text" placeholder="ej: Francia" />
          </div>
          <div class="form-group">
            <label>Calificación (1–5)</label>
            <input v-model.number="form.rating" type="number" min="1" max="5" />
          </div>
        </template>

        <div class="form-group">
          <label>Notas (opcional)</label>
          <textarea v-model="form.notes" rows="3" placeholder="Comentarios libres…" />
        </div>

        <p v-if="error" class="error-msg">{{ error }}</p>
        <div style="display:flex; gap:1rem; margin-top:0.5rem">
          <button type="submit" class="btn btn-primary">{{ isEditing ? 'Guardar cambios' : 'Registrar' }}</button>
          <RouterLink to="/entries" class="btn">Cancelar</RouterLink>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useEntriesStore } from '@/stores/entries'
import api from '@/api/client'

const route = useRoute()
const router = useRouter()
const store = useEntriesStore()

const isEditing = computed(() => !!route.params.id)
const error = ref('')

const form = ref({
  category: '', title: '', date: '', notes: null,
  rating: null, saga_name: null, saga_part: null,
  season_number: null, country: null, city: null, place_type: null,
})

const titleLabel = computed(() => {
  const labels = { city: 'Ciudad', place: 'Nombre del lugar', event: 'Nombre del evento', movie_series: 'Título', book: 'Título' }
  return labels[form.value.category] || 'Título'
})
const titlePlaceholder = computed(() => {
  const ph = { city: 'ej: Venecia', place: "ej: Musée d'Orsay", event: 'ej: Coldplay World Tour', movie_series: 'ej: Dune: Parte Dos', book: 'ej: El nombre del viento' }
  return ph[form.value.category] || ''
})

function resetCategoryFields() {
  Object.assign(form.value, { saga_name: null, saga_part: null, season_number: null, country: null, city: null, place_type: null, rating: null })
}

onMounted(async () => {
  if (isEditing.value) {
    const res = await api.get(`/entries/${route.params.id}`)
    Object.assign(form.value, res.data)
    form.value.date = res.data.date
  }
})

async function submit() {
  error.value = ''
  const payload = Object.fromEntries(Object.entries(form.value).filter(([, v]) => v !== null && v !== ''))
  try {
    if (isEditing.value) {
      await store.updateEntry(route.params.id, payload)
    } else {
      await store.createEntry(payload)
    }
    router.push('/entries')
  } catch (e) {
    error.value = e.response?.data?.detail || 'Error al guardar'
  }
}
</script>
