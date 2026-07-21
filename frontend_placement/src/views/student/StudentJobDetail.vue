<template>
  <div class="container mt-4 d-flex justify-content-center">
    <div v-if="isLoading" class="text-center mt-5">
      <div class="spinner-border text-dark" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>
    <div v-else-if="job" class="card shadow-sm border-0 w-100" style="max-width: 800px;">
      <div class="card-body p-5">
        <div class="mb-4">
          <router-link to="/student/home" class="back-btn">Back to Dashboard</router-link>
        </div>
        
        <h3 class="fw-bold mb-4 text-dark">{{ job.company_name }} - {{ job.title }}</h3>

        <div v-if="!job.is_eligible" class="alert alert-danger mb-4">
          <strong class="d-block mb-2">Not Eligible to Apply</strong>
          <ul class="mb-0">
            <li v-for="reason in job.reasons" :key="reason">{{ reason }}</li>
          </ul>
        </div>

        <div class="row mb-3">
          <div class="col-md-4 fw-semibold text-muted">CTC</div>
          <div class="col-md-8 text-dark fw-medium">₹{{ job.ctc }} LPA</div>
        </div>

        <div class="row mb-3">
          <div class="col-md-4 fw-semibold text-muted">Deadline</div>
          <div class="col-md-8 text-dark">{{ job.deadline }}</div>
        </div>

        <div class="row mb-3">
          <div class="col-md-4 fw-semibold text-muted">Skills Required</div>
          <div class="col-md-8 text-dark">{{ job.skills_required || 'None specified' }}</div>
        </div>

        <div class="row mb-3">
          <div class="col-md-4 fw-semibold text-muted">Minimum CGPA</div>
          <div class="col-md-8 text-dark">{{ job.min_cgpa }}</div>
        </div>

        <div class="row mb-4">
          <div class="col-md-4 fw-semibold text-muted">Job Description</div>
          <div class="col-md-8">
            <a v-if="job.jd_filename" :href="`http://localhost:8000/api/files/jd/${job.jd_filename}?token=${authState.token}`" target="_blank" class="btn btn-outline-dark btn-sm">
              View JD (PDF)
            </a>
            <span v-else class="text-muted fst-italic">Not provided</span>
          </div>
        </div>

        <hr class="my-4" />

        <div v-if="job.is_eligible" class="bg-light p-4 rounded text-center">
          <h5 class="fw-bold mb-3 text-dark">Apply for this Drive</h5>
          <div class="mb-4 text-start">
            <label class="form-label text-dark fw-medium small">Select a Resume to Apply With <span class="text-danger">*</span></label>
            <select class="form-select" v-model="selectedResumeId">
              <option value="" disabled>-- Select a Resume --</option>
              <option v-for="resume in resumes" :key="resume.id" :value="resume.id">
                {{ resume.name }}
              </option>
            </select>
            <div v-if="resumes.length === 0" class="form-text text-danger">
              You haven't uploaded any resumes. Please go to Edit Profile to upload one.
            </div>
          </div>

          <button class="btn btn-primary px-5 py-2" @click="handleApply" :disabled="isApplying || !selectedResumeId">
            <span v-if="isApplying" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
            {{ isApplying ? 'Submitting Application...' : 'Apply Now' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useApi } from '../../composables/useApi'
import { authState } from '../../store/auth'
import { toast } from 'vue3-toastify'
import FileUpload from '../../components/FileUpload.vue'

const route = useRoute()
const router = useRouter()
const { apiFetch } = useApi()

const job = ref(null)
const isLoading = ref(true)
const isApplying = ref(false)

const resumes = ref([])
const selectedResumeId = ref('')

onMounted(async () => {
  try {
    const data = await apiFetch(`/student/jobs/${route.params.id}`)
    job.value = data
    
    // Fetch user's resumes
    const resumeData = await apiFetch('/student/resumes')
    resumes.value = resumeData
    if (resumeData.length > 0) {
      selectedResumeId.value = resumeData[0].id // Auto-select the first one
    }
  } catch (error) {
    toast.error(error.message || 'Failed to load job details.')
  } finally {
    isLoading.value = false
  }
})

const handleApply = async () => {
  isApplying.value = true

  try {
    const payload = {
      resume_id: selectedResumeId.value
    }

    await apiFetch(`/student/jobs/${route.params.id}/apply`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(payload)
    })

    toast.success('Application submitted successfully! Redirecting...')
    setTimeout(() => {
      router.push('/student/home')
    }, 1500)
  } catch (error) {
    toast.error(error.message || 'Failed to apply')
  } finally {
    isApplying.value = false
  }
}
</script>

<style scoped>
</style>
