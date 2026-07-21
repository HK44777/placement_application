<template>
  <div class="container min-vh-100 d-flex align-items-center justify-content-center">
    <div class="text-center">
      <!-- Portal Name -->
      <h1 class="fw-semibold mb-3">College Placement Portal</h1>
      <!-- Tagline -->
      <p class="text-muted mb-4">
        Connecting Students and Companies for Better Opportunities
      </p>
      <!-- Action Buttons -->
      <div class="d-flex gap-3 justify-content-center">
        <router-link to="/login" class="btn btn-dark">
          Login
        </router-link>
        <!-- Register Button (opens modal) -->
        <button
          class="btn btn-outline-dark"
          data-bs-toggle="modal"
          data-bs-target="#registerModal">
          Register
        </button>
      </div>
    </div>
  </div>

  <!-- Register Modal -->
  <div class="modal fade" id="registerModal" tabindex="-1">
    <div class="modal-dialog modal-dialog-centered">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title" id="registerModalLabel">
            Choose Registration Type
          </h5>
          <button
            type="button"
            class="btn-close"
            data-bs-dismiss="modal">
          </button>
        </div>
        <div class="modal-body text-center">
          <div class="d-flex flex-column align-items-center gap-3">
            <button
              @click="navigateTo('/student-register')"
              class="btn btn-dark"
              style="width: 220px;">
              Register as Student
            </button>
            <button
              @click="navigateTo('/company-register')"
              class="btn btn-dark"
              style="width: 220px;">
              Register as Company
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const navigateTo = (path) => {
  // Click the hidden close button to let bootstrap handle the modal cleanup
  const closeBtn = document.querySelector('#registerModal .btn-close')
  if (closeBtn) {
    closeBtn.click()
  }
  
  // Wait for the modal fade animation to finish before pushing the route
  setTimeout(() => {
    router.push(path)
  }, 250)
}
</script>

<style scoped>
</style>
