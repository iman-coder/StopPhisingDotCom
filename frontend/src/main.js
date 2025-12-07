import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import router from './router'
import { initAuthOnStartup, setupInterceptors } from './services/authService.js'

// Bootstrap (CSS only)
import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap-icons/font/bootstrap-icons.css'

// Initialize auth before mounting to avoid racing protected requests on
// first-page load. We await the startup initialization, then register
// interceptors and mount the app.
(async () => {
	await initAuthOnStartup();
	setupInterceptors();
	createApp(App).use(router).mount('#app');
})();
