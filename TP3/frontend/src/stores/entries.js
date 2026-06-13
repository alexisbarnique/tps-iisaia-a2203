import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/api/client'

export const useEntriesStore = defineStore('entries', () => {
  const entries = ref([])

  async function fetchEntries(filters = {}) {
    const res = await api.get('/entries', { params: filters })
    entries.value = res.data
    return res.data
  }

  async function createEntry(data) {
    const res = await api.post('/entries', data)
    entries.value.unshift(res.data)
    return res.data
  }

  async function updateEntry(id, data) {
    const res = await api.put(`/entries/${id}`, data)
    const idx = entries.value.findIndex(e => String(e.id) === String(id))
    if (idx !== -1) entries.value[idx] = res.data
    return res.data
  }

  async function deleteEntry(id) {
    await api.delete(`/entries/${id}`)
    entries.value = entries.value.filter(e => e.id !== id)
  }

  return { entries, fetchEntries, createEntry, updateEntry, deleteEntry }
})
