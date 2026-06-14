<template>
  <div>
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:1.5rem">
      <h1 class="page-title" style="margin-bottom:0">Mis metas</h1>
      <RouterLink to="/goals/new" class="btn btn-primary">+ Nueva meta</RouterLink>
    </div>

    <div v-if="loading" class="muted-text">Cargando…</div>
    <div v-else-if="goals.length === 0" class="muted-text">
      <p>Todavía no tenés metas. ¡Creá la primera!</p>
      <RouterLink to="/goals/new" class="btn btn-primary" style="margin-top:1rem">Crear meta</RouterLink>
    </div>
    <GoalCard
      v-for="goal in goals"
      :key="goal.id"
      :goal="goal"
      @delete="handleDelete"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useGoalsStore } from '@/stores/goals'
import GoalCard from '@/components/GoalCard.vue'

const store = useGoalsStore()
const goals = ref([])
const loading = ref(false)

onMounted(async () => {
  loading.value = true
  goals.value = await store.fetchGoals()
  loading.value = false
})

async function handleDelete(id) {
  if (!confirm('¿Eliminar esta meta?')) return
  await store.deleteGoal(id)
  goals.value = goals.value.filter(g => String(g.id) !== String(id))
}
</script>

<style scoped>
.muted-text { color: var(--color-muted); font-style: italic; text-align: center; padding: 2rem; }
</style>
