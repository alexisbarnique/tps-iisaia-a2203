<template>
  <div>
    <h1 class="page-title">{{ isEditing ? 'Editar meta' : 'Nueva meta' }}</h1>
    <div class="card" style="max-width:480px">
      <form @submit.prevent="submit">
        <div class="form-group">
          <label>Categoría</label>
          <select v-model="form.category" required :disabled="isEditing">
            <option value="">— elegir —</option>
            <option value="event">🎵 Eventos</option>
            <option value="movie_series">🎬 Películas/Series</option>
            <option value="book">📚 Libros</option>
            <option value="city">🗺️ Ciudades</option>
            <option value="place">🏛️ Lugares</option>
          </select>
        </div>

        <div v-if="!isEditing" class="form-group">
          <label>Año</label>
          <input v-model.number="form.year" type="number" min="2020" max="2100" required />
        </div>

        <div class="form-group">
          <label>Objetivo (cantidad)</label>
          <input v-model.number="form.target" type="number" min="1" required placeholder="ej: 12" />
        </div>

        <p v-if="error" class="error-msg">{{ error }}</p>
        <div style="display:flex;gap:1rem;margin-top:0.5rem">
          <button type="submit" class="btn btn-primary">
            {{ isEditing ? 'Guardar cambios' : 'Crear meta' }}
          </button>
          <RouterLink to="/goals" class="btn">Cancelar</RouterLink>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useGoalsStore } from '@/stores/goals'

const route = useRoute()
const router = useRouter()
const store = useGoalsStore()

const isEditing = computed(() => !!route.params.id)
const error = ref('')
const form = ref({ category: '', year: new Date().getFullYear(), target: null })

onMounted(async () => {
  if (!isEditing.value) return
  const goals = store.goals.length ? store.goals : await store.fetchGoals()
  const goal = goals.find(g => String(g.id) === String(route.params.id))
  if (goal) {
    form.value.category = goal.category
    form.value.year = goal.year
    form.value.target = goal.target
  }
})

async function submit() {
  error.value = ''
  try {
    if (isEditing.value) {
      await store.updateGoal(route.params.id, { target: form.value.target })
    } else {
      await store.createGoal({ year: form.value.year, category: form.value.category, target: form.value.target })
    }
    router.push('/goals')
  } catch (e) {
    error.value = e.response?.data?.detail || 'Error al guardar'
  }
}
</script>
