import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'
import UrlsView from '../views/URLs.vue'

const routes = [
    {
        path: '/',
        name: 'dashboard',
        component: Dashboard
    },
    {
        path: '/urls',
        name: 'urls',
        component: UrlsView
    }
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

export default router