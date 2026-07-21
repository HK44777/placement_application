<template>
  <div class="d-flex align-items-center justify-content-center py-5 min-vh-100">
    <div class="card shadow-sm w-100" style="max-width: 520px;">
      <div class="card-body p-4">
        
        <router-link to="/login" class="back-btn mb-3 d-inline-block">Back</router-link>
        
        <h4 class="text-center fw-semibold mb-2 text-dark">
          Company Registration
        </h4>
        <div class="text-center text-muted small mb-4"><span class="text-danger fw-bold">*</span> Indicates a mandatory field</div>

        <form @submit.prevent="handleRegister" novalidate>
          <!-- Login Email -->
          <div class="mb-3">
            <label class="form-label text-dark fw-medium">Login Email <span class="text-danger">*</span></label>
            <input type="email" class="form-control" :class="{'is-invalid': fieldErrors.email}" v-model="form.email" />
            <div v-if="fieldErrors.email" class="invalid-feedback">{{ fieldErrors.email[0] }}</div>
          </div>

          <!-- Password -->
          <div class="mb-3">
            <label class="form-label text-dark fw-medium">Password <span class="text-danger">*</span></label>
            <div class="input-group">
              <input :type="showPassword ? 'text' : 'password'" class="form-control" :class="{'is-invalid': fieldErrors.password, 'border-end-0': true}" v-model="form.password" />
              <button type="button" class="input-group-text password-toggle-btn bg-white" :class="{'border-danger': fieldErrors.password}" @click="showPassword = !showPassword" tabindex="-1">
                <svg v-if="!showPassword" xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" class="bi bi-eye-fill" viewBox="0 0 16 16"><path d="M10.5 8a2.5 2.5 0 1 1-5 0 2.5 2.5 0 0 1 5 0"/><path d="M0 8s3-5.5 8-5.5S16 8 16 8s-3 5.5-8 5.5S0 8 0 8m8 3.5a3.5 3.5 0 1 0 0-7 3.5 3.5 0 0 0 0 7"/></svg>
                <svg v-else xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" class="bi bi-eye-slash-fill" viewBox="0 0 16 16"><path d="m10.79 12.912-1.614-1.615a3.5 3.5 0 0 1-4.474-4.474l-2.06-2.06C.938 6.278 0 8 0 8s3 5.5 8 5.5a7 7 0 0 0 2.79-.588M5.21 3.088A7 7 0 0 1 8 2.5c5 0 8 5.5 8 5.5s-.939 1.721-2.641 3.238l-2.09-2.09a3.5 3.5 0 0 0-4.474-4.474z"/><path d="M5.525 7.646a2.5 2.5 0 0 0 2.829 2.829zm4.95.708-2.829-2.83a2.5 2.5 0 0 1 2.829 2.829zm3.171 6-12-12 .708-.708 12 12z"/></svg>
              </button>
            </div>
            <div v-if="fieldErrors.password" class="d-block invalid-feedback">{{ fieldErrors.password[0] }}</div>
          </div>

          <!-- Confirm Password -->
          <div class="mb-3">
            <label class="form-label text-dark fw-medium">Confirm Password <span class="text-danger">*</span></label>
            <div class="input-group">
              <input :type="showConfirmPassword ? 'text' : 'password'" class="form-control" :class="{'is-invalid': fieldErrors.confirmPassword, 'border-end-0': true}" v-model="form.confirmPassword" />
              <button type="button" class="input-group-text password-toggle-btn bg-white" :class="{'border-danger': fieldErrors.confirmPassword}" @click="showConfirmPassword = !showConfirmPassword" tabindex="-1">
                <svg v-if="!showConfirmPassword" xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" class="bi bi-eye-fill" viewBox="0 0 16 16"><path d="M10.5 8a2.5 2.5 0 1 1-5 0 2.5 2.5 0 0 1 5 0"/><path d="M0 8s3-5.5 8-5.5S16 8 16 8s-3 5.5-8 5.5S0 8 0 8m8 3.5a3.5 3.5 0 1 0 0-7 3.5 3.5 0 0 0 0 7"/></svg>
                <svg v-else xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" class="bi bi-eye-slash-fill" viewBox="0 0 16 16"><path d="m10.79 12.912-1.614-1.615a3.5 3.5 0 0 1-4.474-4.474l-2.06-2.06C.938 6.278 0 8 0 8s3 5.5 8 5.5a7 7 0 0 0 2.79-.588M5.21 3.088A7 7 0 0 1 8 2.5c5 0 8 5.5 8 5.5s-.939 1.721-2.641 3.238l-2.09-2.09a3.5 3.5 0 0 0-4.474-4.474z"/><path d="M5.525 7.646a2.5 2.5 0 0 0 2.829 2.829zm4.95.708-2.829-2.83a2.5 2.5 0 0 1 2.829 2.829zm3.171 6-12-12 .708-.708 12 12z"/></svg>
              </button>
            </div>
            <div v-if="fieldErrors.confirmPassword" class="d-block invalid-feedback">{{ fieldErrors.confirmPassword[0] }}</div>
          </div>

          <!-- Company Name -->
          <div class="mb-3">
            <label class="form-label text-dark fw-medium">Company Name <span class="text-danger">*</span></label>
            <input type="text" class="form-control" :class="{'is-invalid': fieldErrors.companyName}" v-model="form.companyName" />
            <div v-if="fieldErrors.companyName" class="invalid-feedback">{{ fieldErrors.companyName[0] }}</div>
          </div>

          <!-- Website -->
          <div class="mb-3">
            <label class="form-label text-dark fw-medium">Website URL <span class="text-danger">*</span></label>
            <input type="url" class="form-control" :class="{'is-invalid': fieldErrors.website}" v-model="form.website" />
            <div v-if="fieldErrors.website" class="invalid-feedback">{{ fieldErrors.website[0] }}</div>
          </div>

          <!-- HR Email -->
          <div class="mb-3">
            <label class="form-label text-dark fw-medium">HR Contact Email <span class="text-danger">*</span></label>
            <input type="email" class="form-control" :class="{'is-invalid': fieldErrors.hrEmail}" v-model="form.hrEmail" />
            <div v-if="fieldErrors.hrEmail" class="invalid-feedback">{{ fieldErrors.hrEmail[0] }}</div>
          </div>

          <!-- Company Type -->
          <div class="mb-4">
            <label class="form-label text-dark fw-medium">Company Type <span class="text-danger">*</span></label>
            <select class="form-select" :class="{'is-invalid': fieldErrors.companyType}" v-model="form.companyType">
              <option value="" disabled>Select company type</option>
              <option value="IT Product">IT Product</option>
              <option value="IT Service">IT Service</option>
              <option value="Core Engineering">Core Engineering</option>
              <option value="Consulting">Consulting</option>
              <option value="Startup">Startup</option>
              <option value="Other">Other</option>
            </select>
            <div v-if="fieldErrors.companyType" class="invalid-feedback">{{ fieldErrors.companyType[0] }}</div>
          </div>

          <!-- Submit -->
          <div class="d-grid mb-3">
            <button type="submit" class="btn btn-primary" :disabled="isLoading">
              <span v-if="isLoading" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
              {{ isLoading ? 'Registering...' : 'Register' }}
            </button>
          </div>
        </form>

        <!-- Login link -->
        <div class="text-center small mt-4">
          <p class="mb-1 text-muted">Already have an account?</p>
          <router-link to="/login" class="text-decoration-none fw-bold text-dark">
            Login here
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useApi } from '../composables/useApi'
import { toast } from 'vue3-toastify'

const router = useRouter()
const { apiFetch } = useApi()

const form = ref({
  email: '',
  password: '',
  confirmPassword: '',
  companyName: '',
  website: '',
  hrEmail: '',
  companyType: ''
})

const fieldErrors = ref({})
const isLoading = ref(false)
const showPassword = ref(false)
const showConfirmPassword = ref(false)

const handleRegister = async () => {
  fieldErrors.value = {}
  let isValid = true

  if (!form.value.email.trim()) {
    fieldErrors.value.email = ['A valid corporate email address is required for registration.']
    isValid = false
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.value.email)) {
    fieldErrors.value.email = ['Please provide a valid email format (e.g. hr@company.com).']
    isValid = false
  }

  if (!form.value.password) {
    fieldErrors.value.password = ['Please create a secure password.']
    isValid = false
  } else if (form.value.password.length < 8) {
    fieldErrors.value.password = ['Password must be at least 8 characters long.']
    isValid = false
  }

  if (!form.value.confirmPassword) {
    fieldErrors.value.confirmPassword = ['Please confirm your password.']
    isValid = false
  } else if (form.value.password !== form.value.confirmPassword) {
    fieldErrors.value.confirmPassword = ['The passwords entered do not match. Please verify.']
    isValid = false
  }

  if (!form.value.companyName.trim()) {
    fieldErrors.value.companyName = ['Your registered company name is required.']
    isValid = false
  }

  if (!form.value.website.trim()) {
    fieldErrors.value.website = ['Please provide your official company website.']
    isValid = false
  } else if (!/^https?:\/\/.+/.test(form.value.website)) {
    fieldErrors.value.website = ['Please provide a valid website URL starting with http:// or https://.']
    isValid = false
  }

  if (!form.value.hrEmail.trim()) {
    fieldErrors.value.hrEmail = ['A valid HR contact email is necessary for official communication.']
    isValid = false
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.value.hrEmail)) {
    fieldErrors.value.hrEmail = ['Please provide a valid HR email format.']
    isValid = false
  }

  if (!form.value.companyType) {
    fieldErrors.value.companyType = ["Please specify your organization's industry type."]
    isValid = false
  }

  if (!isValid) {
    toast.error('Please correct the highlighted fields.')
    return
  }

  isLoading.value = true

  try {
    const data = await apiFetch('/auth/register/company', {
      method: 'POST',
      body: JSON.stringify({
        email: form.value.email,
        password: form.value.password,
        confirm_password: form.value.confirmPassword,
        company_name: form.value.companyName,
        website: form.value.website,
        hr_contact: form.value.hrEmail,
        company_type: form.value.companyType
      })
    })

    router.push({ path: '/login', state: { companyRegistered: true } })
  } catch (error) {
    if (error.validationErrors) {
      if (error.validationErrors.email) fieldErrors.value.email = error.validationErrors.email
      if (error.validationErrors.password) fieldErrors.value.password = error.validationErrors.password
      if (error.validationErrors.confirm_password) fieldErrors.value.confirmPassword = error.validationErrors.confirm_password
      if (error.validationErrors.company_name) fieldErrors.value.companyName = error.validationErrors.company_name
      if (error.validationErrors.website) fieldErrors.value.website = error.validationErrors.website
      if (error.validationErrors.hr_contact) fieldErrors.value.hrEmail = error.validationErrors.hr_contact
      if (error.validationErrors.company_type) fieldErrors.value.companyType = error.validationErrors.company_type
      toast.error('Please correct the highlighted fields.')
    } else {
      toast.error(error.message || 'Registration failed')
    }
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
</style>
