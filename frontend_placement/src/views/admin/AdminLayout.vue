<template>
  <div class="bg-light min-vh-100">
    <nav class="navbar navbar-expand-lg bg-white navbar-light border-bottom mb-4 shadow-sm">
      <div class="container">
        <span class="navbar-brand fw-semibold text-dark">
          <i class="bi bi-shield-lock-fill me-2"></i> Admin Control Panel
        </span>
        
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#adminNavbar">
          <span class="navbar-toggler-icon"></span>
        </button>

        <div class="collapse navbar-collapse" id="adminNavbar">
          <ul class="navbar-nav me-auto mb-2 mb-lg-0">
            <li class="nav-item">
              <router-link to="/admin/dashboard" class="nav-link" active-class="active">Dashboard</router-link>
            </li>
            <li class="nav-item">
              <router-link to="/admin/companies" class="nav-link" active-class="active">Companies</router-link>
            </li>
            <li class="nav-item">
              <router-link to="/admin/students" class="nav-link" active-class="active">Students</router-link>
            </li>
            <li class="nav-item">
              <router-link to="/admin/drives" class="nav-link" active-class="active">Drives</router-link>
            </li>
          </ul>
          <div class="d-flex">
            <button class="btn btn-outline-dark btn-sm" @click="handleLogout">Logout</button>
          </div>
        </div>
      </div>
    </nav>
    
    <!-- Render the current admin page -->
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

const isLoading = ref(true)

const fetchMe = async () => {
  try {
    // Just verify the token/role is still valid
    await apiFetch('/auth/me')
  } catch (error) {
    console.error("Failed to authenticate admin:", error)
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
.navbar-nav .nav-link.active {
  font-weight: 600;
  border-bottom: 2px solid #000;
}
</style>
