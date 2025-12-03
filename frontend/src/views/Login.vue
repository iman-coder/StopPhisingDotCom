<template>
  <div class="login-page container" style="max-width:420px; margin-top:40px">
    <div class="card p-4">
      <h4 class="mb-3">Sign In</h4>

      <form @submit.prevent="submit">
        <div class="mb-2">
          <input v-model="username" class="form-control" placeholder="Username" required />
        </div>
        <div class="mb-3">
          <input v-model="password" type="password" class="form-control" placeholder="Password" required />
        </div>

        <div v-if="error" class="alert alert-danger" role="alert">{{ error }}</div>

        <div class="d-grid">
          <button class="btn btn-primary" :disabled="loading">
            <span v-if="loading" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
            Sign In
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { login } from '../services/authService.js'

export default {
  name: 'LoginView',
  setup() {
    const username = ref('')
    const password = ref('')
    const loading = ref(false)
    const error = ref('')
    const router = useRouter()

    async function submit() {
      error.value = ''
      loading.value = true
      try {
        await login(username.value, password.value)
        // on success redirect to dashboard
        router.push({ name: 'dashboard' })
      } catch (err) {
        console.error(err)
        // try to show a readable message
        if (err.response && err.response.data && err.response.data.detail) {
          error.value = err.response.data.detail
        } else {
          error.value = 'Login failed. Check credentials and backend connectivity.'
        }
      } finally {
        loading.value = false
      }
    }

    return { username, password, loading, error, submit }
  }
}
</script>

<style scoped>
.login-page { padding: 16px; }
</style>
