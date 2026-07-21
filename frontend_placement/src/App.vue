<script setup>
import { onMounted } from 'vue'
import { useApi } from './composables/useApi'
import GlobalModals from './components/GlobalModals.vue'

const { apiFetch } = useApi()

onMounted(async () => {
  // Proactive boot check: if there's any sign of a session, try to validate it immediately
  if (localStorage.getItem('access_token') || document.cookie.includes('refresh_token')) {
    try {
      await apiFetch('/auth/me')
    } catch (error) {
      // useApi.js handles 401s by trying to refresh, and if that fails, it clears auth and redirects.
      console.log('Session validation failed or expired.')
    }
  }
})
</script>

<template>
  <router-view />
  <GlobalModals />
</template>

<style>
/* Global styles can go here, but we are using Bootstrap in index.html */
</style>
