<template>
  <div class="container mt-4 d-flex justify-content-center">
    <div v-if="isFetching" class="text-center mt-5">Loading...</div>
    <div v-else class="card shadow-sm border-0" style="width: 70%;">
      <div class="card-body p-5">
        <h5 class="card-title fw-semibold mb-4 text-center">Edit Profile</h5>

        <form @submit.prevent="handleSave" novalidate>
          <div class="mb-3">
            <label class="form-label fw-semibold text-muted">Full Name</label>
            <input type="text" class="form-control" :class="{'is-invalid': fieldErrors.name}" v-model="form.name" />
            <div v-if="fieldErrors.name" class="invalid-feedback">{{ fieldErrors.name[0] }}</div>
          </div>

          <div class="mb-3">
            <label class="form-label fw-semibold text-muted">CGPA</label>
            <input type="number" step="0.01" class="form-control" :class="{'is-invalid': fieldErrors.cgpa}" v-model="form.cgpa" />
            <div v-if="fieldErrors.cgpa" class="invalid-feedback">{{ fieldErrors.cgpa[0] }}</div>
          </div>

          <div class="mb-3">
            <label class="form-label fw-semibold text-muted">Backlog History</label>
            <select class="form-select" :class="{'is-invalid': fieldErrors.backlog_history}" v-model="form.backlogHistory">
              <option value="Yes">Yes</option>
              <option value="No">No</option>
            </select>
            <div v-if="fieldErrors.backlog_history" class="invalid-feedback">{{ fieldErrors.backlog_history[0] }}</div>
          </div>

          <div class="mb-3">
            <label class="form-label fw-semibold text-muted">Active Backlogs</label>
            <input type="number" class="form-control" :class="{'is-invalid': fieldErrors.active_backlog}" v-model="form.activeBacklog" />
            <div v-if="fieldErrors.active_backlog" class="invalid-feedback">{{ fieldErrors.active_backlog[0] }}</div>
          </div>

          <div class="mb-3">
            <label class="form-label fw-semibold text-muted">Skills</label>
            <SkillSelector v-model="form.skills" :class="{'is-invalid': fieldErrors.skills}" />
            <div v-if="fieldErrors.skills" class="invalid-feedback d-block">{{ fieldErrors.skills[0] }}</div>
          </div>

          <!-- Removed Single Resume Upload -->


          <div class="d-grid mt-4">
            <button type="submit" class="btn btn-primary" :disabled="isSaving">
              {{ isSaving ? 'Saving...' : 'Save Changes' }}
            </button>
          </div>
        </form>

        <div class="text-center mt-3 small">
          <router-link to="/student/profile" class="text-decoration-none text-dark fw-medium">
            Cancel & Back to Profile
          </router-link>
        </div>
      </div>
    </div>

    <div v-if="!isFetching" class="card shadow-sm border-0 mt-4 mb-5" style="width: 70%;">
      <div class="card-body p-5">
        <h5 class="card-title fw-semibold mb-4 text-center">Manage Resumes</h5>
        
        <div v-if="isFetchingResumes" class="text-center my-3">
          <div class="spinner-border spinner-border-sm text-dark" role="status"></div>
        </div>
        
        <div v-else class="mb-5">
          <div v-if="resumes.length === 0" class="text-muted text-center p-3 bg-light rounded">
            No resumes found.
          </div>
          <div v-else class="list-group">
            <div v-for="resume in resumes" :key="resume.id" class="list-group-item d-flex justify-content-between align-items-center">
              <div>
                <div class="fw-bold text-dark">{{ resume.name }}</div>
                <div class="small text-muted">Uploaded: {{ new Date(resume.created_at).toLocaleDateString() }}</div>
              </div>
              <div>
                <a :href="`http://localhost:5000/api/files/resumes/${resume.file_path}?token=${authState.token}`" target="_blank" class="btn btn-sm btn-outline-secondary me-2">View</a>
                <button @click="promptDelete(resume.id)" class="btn btn-sm btn-outline-danger" data-bs-toggle="modal" data-bs-target="#deleteConfirmModal" :disabled="isDeleting === resume.id">
                  <span v-if="isDeleting === resume.id" class="spinner-border spinner-border-sm" role="status"></span>
                  <span v-else>Delete</span>
                </button>
              </div>
            </div>
          </div>
        </div>

        <h6 class="fw-bold mb-3 border-bottom pb-2">Upload New Resume</h6>
        <form @submit.prevent="handleUploadResume" novalidate class="bg-light p-4 rounded">
          <div class="mb-3">
            <label class="form-label fw-semibold text-muted">Resume Name</label>
            <input type="text" class="form-control" v-model="newResume.name" placeholder="e.g., SDE Resume" required />
          </div>
          <div class="mb-3">
            <label class="form-label fw-semibold text-muted">Resume File (PDF)</label>
            <FileUpload v-model="newResume.file" accept=".pdf" />
          </div>
          <div class="d-flex justify-content-end">
            <button type="submit" class="btn btn-dark" :disabled="isUploading || !newResume.name || !newResume.file">
              <span v-if="isUploading" class="spinner-border spinner-border-sm me-2" role="status"></span>
              {{ isUploading ? 'Uploading...' : 'Upload Resume' }}
            </button>
          </div>
        </form>

      </div>
    </div>
    
    <!-- Delete Confirmation Modal -->
    <div class="modal fade" id="deleteConfirmModal" tabindex="-1" aria-hidden="true">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content border-0 shadow">
          <div class="modal-header border-bottom-0 pb-0">
            <h5 class="modal-title fw-bold text-danger">Delete Resume</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body py-4">
            Are you sure you want to delete this resume? This action cannot be undone.
          </div>
          <div class="modal-footer border-top-0 pt-0">
            <button type="button" class="btn btn-light" data-bs-dismiss="modal">Cancel</button>
            <button type="button" class="btn btn-danger px-4" @click="confirmDelete" :disabled="isDeleting">
              <span v-if="isDeleting" class="spinner-border spinner-border-sm me-2" role="status"></span>
              {{ isDeleting ? 'Deleting...' : 'Delete' }}
            </button>
          </div>
        </div>
      </div>
    </div>
    
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useApi } from '../../composables/useApi'
import { authState } from '../../store/auth'
import { toast } from 'vue3-toastify'
import FileUpload from '../../components/FileUpload.vue'
import SkillSelector from '../../components/SkillSelector.vue'

const router = useRouter()
const { apiFetch } = useApi()

const form = ref({
  name: '',
  cgpa: '',
  backlogHistory: 'No',
  activeBacklog: 0,
  skills: ''
})

const isFetching = ref(true)
const isSaving = ref(false)
const fieldErrors = ref({})

// Resume Management State
const resumes = ref([])
const isFetchingResumes = ref(false)
const isUploading = ref(false)
const isDeleting = ref(null)
const resumeToDelete = ref(null)
const newResume = ref({
  name: '',
  file: null
})

onMounted(async () => {
  try {
    const data = await apiFetch('/student/profile')
    form.value.name = data.name
    form.value.cgpa = data.cgpa
    form.value.backlogHistory = data.backlog_history
    form.value.activeBacklog = data.active_backlog
    form.value.skills = data.skills || ''
    
    await fetchResumes()
  } catch (error) {
    toast.error("Failed to load profile.")
  } finally {
    isFetching.value = false
  }
})

const fetchResumes = async () => {
  isFetchingResumes.value = true
  try {
    const data = await apiFetch('/student/resumes')
    resumes.value = data
  } catch (err) {
    toast.error("Failed to fetch resumes")
  } finally {
    isFetchingResumes.value = false
  }
}

const handleUploadResume = async () => {
  isUploading.value = true
  try {
    const formData = new FormData()
    formData.append('name', newResume.value.name)
    formData.append('resume', newResume.value.file)

    await apiFetch('/student/resumes', {
      method: 'POST',
      body: formData
    })
    
    toast.success('Resume uploaded successfully!')
    newResume.value.name = ''
    newResume.value.file = null
    await fetchResumes()
  } catch (err) {
    toast.error(err.message || 'Failed to upload resume')
  } finally {
    isUploading.value = false
  }
}

const promptDelete = (id) => {
  resumeToDelete.value = id
}

const confirmDelete = async () => {
  if (!resumeToDelete.value) return
  
  isDeleting.value = resumeToDelete.value
  try {
    await apiFetch(`/student/resumes/${resumeToDelete.value}`, { method: 'DELETE' })
    toast.success('Resume deleted successfully')
    await fetchResumes()
    
    // Hide modal
    const modalEl = document.getElementById('deleteConfirmModal')
    if (modalEl && window.bootstrap) {
      const bsModal = window.bootstrap.Modal.getInstance(modalEl) || new window.bootstrap.Modal(modalEl)
      bsModal.hide()
    }
  } catch (err) {
    toast.error(err.message || 'Failed to delete resume')
  } finally {
    isDeleting.value = null
    resumeToDelete.value = null
  }
}

const handleSave = async () => {
  fieldErrors.value = {}
  let isValid = true

  if (!form.value.name.trim()) {
    fieldErrors.value.name = ['Your full name cannot be left blank.']
    isValid = false
  }

  if (form.value.cgpa === '' || form.value.cgpa === null) {
    fieldErrors.value.cgpa = ['Please provide an accurate, updated CGPA.']
    isValid = false
  } else if (isNaN(form.value.cgpa) || form.value.cgpa < 0 || form.value.cgpa > 10) {
    fieldErrors.value.cgpa = ['Please enter a valid CGPA between 0 and 10.']
    isValid = false
  }

  if (form.value.activeBacklog === '' || form.value.activeBacklog === null) {
    fieldErrors.value.active_backlog = ['Please correctly specify your active backlog count.']
    isValid = false
  } else if (isNaN(form.value.activeBacklog) || form.value.activeBacklog < 0) {
    fieldErrors.value.active_backlog = ['Active backlog count must be 0 or greater.']
    isValid = false
  }

  if (!isValid) {
    toast.error('Please correct the highlighted fields.')
    return
  }

  isSaving.value = true
  
  try {
    const formData = new FormData()
    formData.append('name', form.value.name)
    formData.append('cgpa', form.value.cgpa)
    formData.append('backlog_history', form.value.backlogHistory)
    formData.append('active_backlog', form.value.activeBacklog)
    formData.append('skills', form.value.skills)

    await apiFetch('/student/profile', {
      method: 'PUT',
      body: formData
    })
    
    toast.success('Profile updated successfully! Redirecting...')
    setTimeout(() => {
      router.push('/student/profile')
    }, 2500)
  } catch (error) {
    if (error.validationErrors) {
      if (error.validationErrors.name) fieldErrors.value.name = error.validationErrors.name
      if (error.validationErrors.cgpa) fieldErrors.value.cgpa = error.validationErrors.cgpa
      if (error.validationErrors.backlog_history) fieldErrors.value.backlog_history = error.validationErrors.backlog_history
      if (error.validationErrors.active_backlog) fieldErrors.value.active_backlog = error.validationErrors.active_backlog
      if (error.validationErrors.skills) fieldErrors.value.skills = error.validationErrors.skills
      toast.error('Please correct the highlighted fields.')
    } else {
      toast.error(error.message || 'Failed to save profile')
    }
  } finally {
    isSaving.value = false
  }
}
</script>

<style scoped>
</style>
