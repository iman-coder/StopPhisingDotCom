import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  server: {
    host: true, // --host (listen on network)
    port: 5173,
    strictPort: false,
    proxy: {
      // Proxy backend endpoints used by the frontend but bypass proxy for
      // browser navigation requests (Accept: text/html). This prevents
      // SPA route refreshes (e.g. /urls) from being forwarded to the API.
      '/urls': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
        bypass: (req, res) => {
          try {
            const accept = req.headers && req.headers.accept
            if (accept && accept.indexOf('text/html') !== -1) return '/index.html'
          } catch (e) {
            // ignore
          }
        }
      },
      '/auth': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
        bypass: (req, res) => {
          try {
            const accept = req.headers && req.headers.accept
            if (accept && accept.indexOf('text/html') !== -1) return '/index.html'
          } catch (e) {
            // ignore
          }
        }
      },
      '/dashboard': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
        bypass: (req, res) => {
          try {
            const accept = req.headers && req.headers.accept
            if (accept && accept.indexOf('text/html') !== -1) return '/index.html'
          } catch (e) {
            // ignore
          }
        }
      }
    }
  }
})
