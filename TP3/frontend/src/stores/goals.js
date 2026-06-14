import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/api/client'

export const useGoalsStore = defineStore('goals', () => {
  const goals = ref([])

  async function fetchGoals() {
    const res = await api.get('/goals')
    goals.value = res.data
    return res.data
  }

  async function createGoal(data) {
    const res = await api.post('/goals', data)
    await fetchGoals()
    return res.data
  }

  async function updateGoal(id, data) {
    const res = await api.put(`/goals/${id}`, data)
    await fetchGoals()
    return res.data
  }

  async function deleteGoal(id) {
    await api.delete(`/goals/${id}`)
    goals.value = goals.value.filter(g => String(g.id) !== String(id))
  }

  return { goals, fetchGoals, createGoal, updateGoal, deleteGoal }
})
