import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../views/dashboard.vue'
import UrlsView from '../views/URLs.vue'
import Login from '../views/Login.vue'
import { isAuthenticated } from '../services/authService'

const routes = [
    {
        path: '/',
        name: 'dashboard',
        component: Dashboard
    },
    {
        path: '/urls',
        name: 'urls',
        component: UrlsView,
        meta: { requiresAuth: true }
    }
    ,
    {
        path: '/login',
        name: 'login',
        component: Login
    }
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

// Global navigation guard: redirect to /login when route requires auth
router.beforeEach((to, from, next) => {
    const requiresAuth = to.matched.some(record => record.meta && record.meta.requiresAuth)
    if (requiresAuth && !isAuthenticated()) {
        return next({ name: 'login', query: { redirect: to.fullPath } })
    }

    // If visiting login while authenticated, send to dashboard
    if (to.name === 'login' && isAuthenticated()) {
        return next({ name: 'dashboard' })
    }

    return next()
})

export default router