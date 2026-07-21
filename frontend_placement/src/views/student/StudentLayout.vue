<template>
  <div class="bg-light min-vh-100">
    <nav class="navbar bg-white border-bottom mb-4 shadow-sm">
      <div class="container">
        <span class="navbar-brand fw-semibold text-dark">
          Student Dashboard
        </span>

        <div class="dropdown">
          <button class="btn btn-dark dropdown-toggle" data-bs-toggle="dropdown">
            {{ user ? user.name : 'My Account' }}
          </button>
          <ul class="dropdown-menu dropdown-menu-end">
            <li>
              <router-link class="dropdown-item" to="/student/profile">Profile</router-link>
            </li>
            <li>
              <router-link class="dropdown-item" to="/student/home">Dashboard Home</router-link>
            </li>
            <li>
              <hr class="dropdown-divider">
            </li>
            <li>
              <button class="dropdown-item text-danger" @click="handleLogout">Logout</button>
            </li>
          </ul>
        </div>
      </div>
    </nav>
    
    <!-- Render the current student page -->
    <div v-if="isLoading" class="text-center mt-5">Loading...</div>
    <router-view v-else />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useApi } from '../../composables/useApi'
import { clearAuth } from '../../store/auth'

const router = useRouter()
const { apiFetch } = useApi()

const user = ref(null)
const isLoading = ref(true)

const fetchMe = async () => {
  try {
    const data = await apiFetch('/auth/me')
    user.value = data
  } catch (error) {
    console.error("Failed to fetch user:", error)
    // Error is handled by apiFetch (redirects to login)
  } finally {
    isLoading.value = false
  }
}

const handleLogout = async () => {
  try {
    await apiFetch('/auth/logout', { method: 'POST' })
  } catch (err) {
    console.error("Logout error", err)
  } finally {
    clearAuth()
    router.push('/login')
  }
}

onMounted(() => {
  fetchMe()
})
</script>

<style scoped>
</style>
