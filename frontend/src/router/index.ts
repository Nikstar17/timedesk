import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import LoginView from '../views/LoginView.vue'
import { checkAuth } from '@/utils/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
      meta: { requiresAuth: true },
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView,
      meta: { guest: true },
    },
  ],
})

// Improved navigation guard
router.beforeEach(async (to, from, next) => {
  const isAuthenticated = await checkAuth()

  // Require authentication for pages that need it
  if (to.matched.some((record) => record.meta.requiresAuth)) {
    if (!isAuthenticated) {
      return next({ path: '/login' })
    }
    return next()
  }

  // Redirect away from login if already authenticated
  if (to.matched.some((record) => record.meta.guest) && isAuthenticated) {
    return next({ path: '/' })
  }

  next()
})

export default router
