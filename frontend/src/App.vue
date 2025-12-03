<template>
  <div>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark px-3">
      <a class="navbar-brand" href="#">StopPhishingdotcom</a>

      <div class="navbar-nav me-auto">
        <router-link to="/" class="nav-link">Dashboard</router-link>
        <router-link to="/urls" class="nav-link">Manage URLs</router-link>
      </div>

      <div class="d-flex align-items-center">
        <div v-if="authenticated" class="text-light me-3">
          <i class="bi bi-person-circle me-1"></i>
          {{ username }}
        </div>
        <router-link v-if="!authenticated" to="/login" class="btn btn-outline-light btn-sm me-2">Sign In</router-link>
        <button v-if="authenticated" @click="doLogout" class="btn btn-outline-light btn-sm">Logout</button>
      </div>
    </nav>

    <div class="container mt-4">
      <router-view />
    </div>
  </div>
</template>
<script>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { isAuthenticated, getUsername, logout } from './services/authService.js'

export default {
  setup() {
    const authenticated = ref(false)
    const username = ref('')
    const router = useRouter()

    function refresh() {
      authenticated.value = isAuthenticated()
      username.value = authenticated.value ? getUsername() : ''
    }

    function doLogout() {
      logout()
      refresh()
      router.push({ name: 'login' })
    }

    onMounted(refresh)

    return { authenticated, username, doLogout }
  }
}
</script>

<style>
.navbar-nav .nav-link { margin-right: 8px }
</style>

<!--The api endpoints:
POST /urls/import
GET /urls/export
GET /urls
POST /urls
DELETE /urls/{id}
PUT /urls/{id} -->
