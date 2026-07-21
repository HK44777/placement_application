<template>
  <div class="container mt-4 mb-5">
    <div v-if="isLoading" class="text-center mt-5">
      <div class="spinner-border text-dark" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>
    
    <div v-else-if="error" class="alert alert-danger text-center">
      {{ error }}
    </div>

    <div v-else class="row justify-content-center">
      <div class="col-md-8">
        <div class="card border-0 shadow-sm">
          <div class="card-header bg-white border-bottom-0 pt-4 pb-0 text-center">
            <h4 class="fw-bold mb-0">Company Profile</h4>
          </div>
          <div class="card-body p-5">
            

            <!-- Profile Details -->
            <div class="row mb-3">
              <div class="col-sm-4 text-muted fw-semibold">Company Name</div>
              <div class="col-sm-8 text-dark">{{ profile.company_name }}</div>
            </div>
            <hr class="text-muted opacity-25">

            <div class="row mb-3">
              <div class="col-sm-4 text-muted fw-semibold">Company Type</div>
              <div class="col-sm-8 text-dark">{{ profile.company_type || 'N/A' }}</div>
            </div>
            <hr class="text-muted opacity-25">

            <div class="row mb-3">
              <div class="col-sm-4 text-muted fw-semibold">Website</div>
              <div class="col-sm-8">
                <a v-if="profile.website" :href="profile.website" target="_blank" class="text-dark text-decoration-none fw-medium">
                  {{ profile.website }} <i class="bi bi-box-arrow-up-right ms-1 small"></i>
                </a>
                <span v-else class="text-muted">N/A</span>
              </div>
            </div>
            <hr class="text-muted opacity-25">

            <div class="row mb-3">
              <div class="col-sm-4 text-muted fw-semibold">HR Contact</div>
              <div class="col-sm-8 text-dark">{{ profile.hr_contact }}</div>
            </div>
            <hr class="text-muted opacity-25">

            <div class="row mb-3">
              <div class="col-sm-4 text-muted fw-semibold">Login Email</div>
              <div class="col-sm-8 text-dark">{{ profile.email }}</div>
            </div>

            <!-- Stats -->
            <div class="row mt-5 pt-3 border-top">
              <div class="col-6 text-center">
                <h3 class="fw-bold text-dark mb-0">{{ profile.total_drives }}</h3>
                <div class="small text-muted text-uppercase fw-semibold">Total Drives</div>
              </div>
              <div class="col-6 text-center">
                <h3 class="fw-bold text-dark mb-0">{{ profile.total_applicants }}</h3>
                <div class="small text-muted text-uppercase fw-semibold">Total Applicants</div>
              </div>
            </div>

            <!-- Edit Button (Only if Rejected) -->
            <div v-if="profile.approval_status === 'Rejected'" class="text-center mt-5">
              <router-link to="/company/profile/edit" class="btn btn-outline-danger px-5">
                Edit Profile
              </router-link>
            </div>

          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useApi } from '../../composables/useApi'

const { apiFetch } = useApi()
const profile = ref(null)
const isLoading = ref(true)
const error = ref('')

const fetchProfile = async () => {
  try {
    const data = await apiFetch('/company/profile')
    profile.value = data
  } catch (err) {
    error.value = err.message || 'Failed to fetch profile'
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  fetchProfile()
})
</script>
