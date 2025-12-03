import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import router from './router'
import { initAuthOnStartup, setupInterceptors } from './services/authService.js'

// Bootstrap (CSS only)
import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap-icons/font/bootstrap-icons.css'

// Initialize auth: attach header, populate current user, and register interceptors
initAuthOnStartup();
setupInterceptors();

createApp(App).use(router).mount('#app')
