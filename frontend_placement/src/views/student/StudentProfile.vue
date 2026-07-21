<template>
  <div class="container mt-4 d-flex flex-column align-items-center">
    
    <div class="w-100 mb-3" style="max-width: 70%;">
      <button class="btn btn-outline-secondary btn-sm" @click="$router.push('/student/home')">
        <i class="bi bi-arrow-left"></i> Back to Dashboard
      </button>
    </div>

    <div v-if="isLoading" class="text-center mt-5">Loading Profile...</div>
    <div v-else-if="profile" class="card shadow-sm border-0 w-100" style="max-width: 70%;">
      <div class="card-body p-5">
        <div class="d-flex justify-content-between align-items-center mb-4">
          <h5 class="card-title fw-semibold m-0">Profile Details</h5>
          <router-link to="/student/profile/edit" class="btn btn-dark btn-sm">
            Edit Profile
          </router-link>
        </div>

        <div class="row mb-3">
          <div class="col-md-4 fw-semibold text-muted">Name</div>
          <div class="col-md-8">{{ profile.name }}</div>
        </div>

        <div class="row mb-3">
          <div class="col-md-4 fw-semibold text-muted">USN</div>
          <div class="col-md-8">{{ profile.usn }}</div>
        </div>

        <div class="row mb-3">
          <div class="col-md-4 fw-semibold text-muted">Branch</div>
          <div class="col-md-8">{{ profile.branch }}</div>
        </div>

        <div class="row mb-3">
          <div class="col-md-4 fw-semibold text-muted">CGPA</div>
          <div class="col-md-8">{{ profile.cgpa }}</div>
        </div>

        <div class="row mb-3">
          <div class="col-md-4 fw-semibold text-muted">Graduation Year</div>
          <div class="col-md-8">{{ profile.graduation_year }}</div>
        </div>

        <div class="row mb-3">
          <div class="col-md-4 fw-semibold text-muted">Backlog History</div>
          <div class="col-md-8">{{ profile.backlog_history }}</div>
        </div>

        <div class="row mb-3">
          <div class="col-md-4 fw-semibold text-muted">Active Backlogs</div>
          <div class="col-md-8">{{ profile.active_backlog }}</div>
        </div>

        <div class="row mb-3">
          <div class="col-md-4 fw-semibold text-muted">Skills</div>
          <div class="col-md-8">
            <span v-if="profile.skills">
              <span v-for="skill in profile.skills.split(',')" :key="skill" class="badge bg-secondary text-white me-1 mb-1">
                {{ skill.trim() }}
              </span>
            </span>
            <span v-else class="text-muted">Not specified</span>
          </div>
        </div>

        <div class="row mb-3">
          <div class="col-md-4 fw-semibold text-muted">Resumes</div>
          <div class="col-md-8">
            <div v-if="resumes.length > 0" class="d-flex flex-wrap gap-2">
              <a v-for="res in resumes" :key="res.id" :href="`http://localhost:5000/api/files/resumes/${res.file_path}?token=${authState.token}`" target="_blank" class="btn btn-outline-dark btn-sm d-flex align-items-center gap-1">
                <i class="bi bi-file-earmark-pdf"></i> {{ res.name }}
              </a>
            </div>
            <span v-else class="text-muted">No resumes uploaded</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useApi } from '../../composables/useApi'
import { authState } from '../../store/auth'

const { apiFetch } = useApi()

const profile = ref(null)
const resumes = ref([])
const isLoading = ref(true)

onMounted(async () => {
  try {
    const data = await apiFetch('/student/profile')
    profile.value = data
    
    // Fetch multiple resumes
    const resumesData = await apiFetch('/student/resumes')
    resumes.value = resumesData || []
  } catch (error) {
    console.error(error)
  } finally {
    isLoading.value = false
  }
})
</script>

<style scoped>
</style>
