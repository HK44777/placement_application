<template>
  <div class="container mt-4 mb-5 d-flex justify-content-center">
    <div v-if="isLoading" class="text-center mt-5">
      <div class="spinner-border text-dark" role="status"></div>
    </div>
    <div v-else class="card shadow-sm border-0 w-100" style="max-width: 600px;">
      <div class="card-body p-5">
        <h4 class="card-title fw-bold text-center mb-4 text-dark">Edit Profile</h4>
        
        <div class="alert alert-warning mb-4 small text-center">
          <i class="bi bi-info-circle me-1"></i> You can only edit your profile because it was rejected. Editing and saving will re-submit your profile for admin approval.
        </div>

        <div v-if="globalError" class="alert alert-danger mb-4 text-center">
          {{ globalError }}
        </div>

        <div v-if="successMessage" class="alert alert-success mb-4 text-center">
          {{ successMessage }}
        </div>

        <form @submit.prevent="handleSave" novalidate>
          <div class="mb-3">
            <label class="form-label text-dark fw-medium">Company Name</label>
            <input type="text" class="form-control" :class="{'is-invalid': fieldErrors.company_name}" v-model="form.company_name" required />
            <div v-if="fieldErrors.company_name" class="invalid-feedback">{{ fieldErrors.company_name[0] }}</div>
          </div>

          <div class="mb-3">
            <label class="form-label text-dark fw-medium">Company Type</label>
            <select class="form-select" :class="{'is-invalid': fieldErrors.company_type}" v-model="form.company_type">
              <option value="" disabled>Select type...</option>
              <option value="IT">IT</option>
              <option value="Core">Core</option>
              <option value="Consulting">Consulting</option>
              <option value="Finance">Finance</option>
              <option value="Other">Other</option>
            </select>
            <div v-if="fieldErrors.company_type" class="invalid-feedback">{{ fieldErrors.company_type[0] }}</div>
          </div>

          <div class="mb-3">
            <label class="form-label text-dark fw-medium">Website</label>
            <input type="url" class="form-control" :class="{'is-invalid': fieldErrors.website}" v-model="form.website" />
            <div v-if="fieldErrors.website" class="invalid-feedback">{{ fieldErrors.website[0] }}</div>
          </div>

          <div class="mb-4">
            <label class="form-label text-dark fw-medium">HR Contact Email / Phone</label>
            <input type="text" class="form-control" :class="{'is-invalid': fieldErrors.hr_contact}" v-model="form.hr_contact" required />
            <div v-if="fieldErrors.hr_contact" class="invalid-feedback">{{ fieldErrors.hr_contact[0] }}</div>
          </div>

          <div class="d-grid gap-2">
            <button type="submit" class="btn btn-dark btn-lg fw-semibold" :disabled="isSaving">
              {{ isSaving ? 'Saving...' : 'Save & Re-submit' }}
            </button>
            <router-link to="/company/profile" class="btn btn-light border mt-2">Cancel</router-link>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useApi } from '../../composables/useApi'

const router = useRouter()
const { apiFetch } = useApi()

const isLoading = ref(true)
const isSaving = ref(false)
const globalError = ref('')
const successMessage = ref('')
const fieldErrors = ref({})

const form = ref({
  company_name: '',
  company_type: '',
  website: '',
  hr_contact: ''
})

const fetchProfile = async () => {
  try {
    const data = await apiFetch('/company/profile')
    // Redirect if not rejected
    if (data.approval_status !== 'Rejected') {
      router.push('/company/profile')
      return
    }
    
    form.value.company_name = data.company_name
    form.value.company_type = data.company_type || ''
    form.value.website = data.website || ''
    form.value.hr_contact = data.hr_contact
  } catch (err) {
    globalError.value = 'Failed to load profile data'
  } finally {
    isLoading.value = false
  }
}

const handleSave = async () => {
  isSaving.value = true
  globalError.value = ''
  successMessage.value = ''
  fieldErrors.value = {}

  try {
    await apiFetch('/company/profile', {
      method: 'PUT',
      body: JSON.stringify(form.value)
    })
    
    successMessage.value = 'Profile updated! Redirecting...'
    setTimeout(() => {
      router.push('/company/profile')
    }, 1500)
  } catch (error) {
    if (error.validationErrors) {
      fieldErrors.value = error.validationErrors
    } else {
      globalError.value = error.message || 'Failed to update profile'
    }
  } finally {
    isSaving.value = false
  }
}

onMounted(() => {
  fetchProfile()
})
</script>
