import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  { path: '/login', component: () => import('@/views/LoginView.vue'), meta: { public: true } },
  { path: '/dashboard', component: () => import('@/views/DashboardView.vue') },
  { path: '/entries', component: () => import('@/views/EntriesListView.vue') },
  { path: '/entries/new', component: () => import('@/views/EntryFormView.vue') },
  { path: '/entries/:id/edit', component: () => import('@/views/EntryFormView.vue') },
  { path: '/summary/monthly', component: () => import('@/views/MonthlySummaryView.vue') },
  { path: '/summary/annual', component: () => import('@/views/AnnualSummaryView.vue') },
  { path: '/', redirect: '/dashboard' },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to) => {
  const auth = useAuthStore()
  if (!to.meta.public && !auth.isAuthenticated) return '/login'
})

export default router
