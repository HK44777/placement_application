<template>
  <div class="d-flex align-items-center justify-content-center py-5 min-vh-100">
    <div class="card shadow-sm w-100" style="max-width: 520px;">
      <div class="card-body p-4">
        
        <router-link to="/login" class="back-btn mb-3 d-inline-block">Back</router-link>
        
        <h4 class="text-center fw-semibold mb-2 text-dark">
          Student Registration
        </h4>
        <div class="text-center text-muted small mb-4"><span class="text-danger fw-bold">*</span> Indicates a mandatory field</div>

        <form @submit.prevent="handleRegister" novalidate>
          <!-- Email -->
          <div class="mb-3">
            <label class="form-label text-dark fw-medium">Email <span class="text-danger">*</span></label>
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

          <!-- Full Name -->
          <div class="mb-3">
            <label class="form-label text-dark fw-medium">Full Name <span class="text-danger">*</span></label>
            <input type="text" class="form-control" :class="{'is-invalid': fieldErrors.name}" v-model="form.name" />
            <div v-if="fieldErrors.name" class="invalid-feedback">{{ fieldErrors.name[0] }}</div>
          </div>

          <!-- USN -->
          <div class="mb-3">
            <label class="form-label text-dark fw-medium">USN <span class="text-danger">*</span></label>
            <input type="text" class="form-control" :class="{'is-invalid': fieldErrors.usn}" v-model="form.usn" />
            <div v-if="fieldErrors.usn" class="invalid-feedback">{{ fieldErrors.usn[0] }}</div>
          </div>

          <!-- Branch -->
          <div class="mb-3">
            <label class="form-label text-dark fw-medium">Branch <span class="text-danger">*</span></label>
            <select class="form-select" :class="{'is-invalid': fieldErrors.branch}" v-model="form.branch">
              <option value="" disabled>Select your branch</option>
              <option value="CSE">Computer Science and Engg (CSE)</option>
              <option value="ISE">Information Science and Engg (ISE)</option>
              <option value="ECE">Electronics and Communication Engg (ECE)</option>
              <option value="MECH">Mechanical Engg (MECH)</option>
              <option value="CIVIL">Civil Engg (CIVIL)</option>
              <option value="EEE">Electrical and Electronics Engg (EEE)</option>
            </select>
            <div v-if="fieldErrors.branch" class="invalid-feedback">{{ fieldErrors.branch[0] }}</div>
          </div>

          <!-- CGPA -->
          <div class="mb-3">
            <label class="form-label text-dark fw-medium">CGPA <span class="text-danger">*</span></label>
            <input type="number" step="0.01" class="form-control" :class="{'is-invalid': fieldErrors.cgpa}" v-model="form.cgpa" />
            <div v-if="fieldErrors.cgpa" class="invalid-feedback">{{ fieldErrors.cgpa[0] }}</div>
          </div>

          <!-- Graduation Year -->
          <div class="mb-3">
            <label class="form-label text-dark fw-medium">Graduation Year <span class="text-danger">*</span></label>
            <select class="form-select" :class="{'is-invalid': fieldErrors.graduationYear}" v-model="form.graduationYear">
              <option value="" disabled>Select graduation year</option>
              <option value="2023">2023</option>
              <option value="2024">2024</option>
              <option value="2025">2025</option>
              <option value="2026">2026</option>
              <option value="2027">2027</option>
              <option value="2028">2028</option>
            </select>
            <div v-if="fieldErrors.graduationYear" class="invalid-feedback">{{ fieldErrors.graduationYear[0] }}</div>
          </div>

          <!-- Backlog History -->
          <div class="mb-3">
            <label class="form-label text-dark fw-medium">Backlog History <span class="text-danger">*</span></label>
            <select class="form-select" :class="{'is-invalid': fieldErrors.backlogHistory}" v-model="form.backlogHistory">
              <option value="No">No, I have never had a backlog</option>
              <option value="Yes">Yes, I had backlogs</option>
            </select>
            <div v-if="fieldErrors.backlogHistory" class="invalid-feedback">{{ fieldErrors.backlogHistory[0] }}</div>
          </div>

          <!-- Active Backlogs -->
          <div class="mb-3">
            <label class="form-label text-dark fw-medium">Active Backlogs <span class="text-danger">*</span></label>
            <input type="number" class="form-control" :class="{'is-invalid': fieldErrors.activeBacklog}" v-model="form.activeBacklog" placeholder="Enter 0 if none" />
            <div v-if="fieldErrors.activeBacklog" class="invalid-feedback">{{ fieldErrors.activeBacklog[0] }}</div>
          </div>

          <!-- Skills -->
          <div class="mb-3">
            <label class="form-label text-dark fw-medium">Skills <span class="text-muted fw-normal">(Optional)</span></label>
            <SkillSelector v-model="form.skills" :class="{'is-invalid': fieldErrors.skills}" />
            <div v-if="fieldErrors.skills" class="invalid-feedback d-block">{{ fieldErrors.skills[0] }}</div>
          </div>

          <!-- Resume Upload -->
          <div class="mb-4">
            <label class="form-label text-dark fw-medium">Resume (PDF) <span class="text-danger">*</span></label>
            <FileUpload v-model="form.resume" accept=".pdf" :error="!!fieldErrors.resume" />
            <div v-if="fieldErrors.resume" class="d-block invalid-feedback">{{ fieldErrors.resume[0] }}</div>
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
import { setAuth } from '../store/auth'
import { toast } from 'vue3-toastify'
import FileUpload from '../components/FileUpload.vue'
import SkillSelector from '../components/SkillSelector.vue'

const router = useRouter()
const { apiFetch } = useApi()

const form = ref({
  email: '',
  password: '',
  confirmPassword: '',
  name: '',
  usn: '',
  branch: '',
  cgpa: '',
  graduationYear: '',
  backlogHistory: 'No',
  activeBacklog: 0,
  skills: '',
  resume: null
})

const fieldErrors = ref({})
const isLoading = ref(false)
const showPassword = ref(false)
const showConfirmPassword = ref(false)

const handleRegister = async () => {
  fieldErrors.value = {}
  let isValid = true

  if (!form.value.email.trim()) {
    fieldErrors.value.email = ['A valid student email address is required.']
    isValid = false
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.value.email)) {
    fieldErrors.value.email = ['Please provide a valid email format.']
    isValid = false
  }

  if (!form.value.password) {
    fieldErrors.value.password = ['A secure password is required for your account.']
    isValid = false
  } else if (form.value.password.length < 8) {
    fieldErrors.value.password = ['Password must be at least 8 characters long.']
    isValid = false
  }

  if (!form.value.confirmPassword) {
    fieldErrors.value.confirmPassword = ['Please confirm your password.']
    isValid = false
  } else if (form.value.password !== form.value.confirmPassword) {
    fieldErrors.value.confirmPassword = ['The passwords entered do not match.']
    isValid = false
  }

  if (!form.value.name.trim()) {
    fieldErrors.value.name = ['Your full legal name is required.']
    isValid = false
  }

  if (!form.value.usn.trim()) {
    fieldErrors.value.usn = ['Your University Seat Number (USN) is mandatory.']
    isValid = false
  }

  if (!form.value.branch) {
    fieldErrors.value.branch = ['Please select your academic branch.']
    isValid = false
  }

  if (form.value.cgpa === '' || form.value.cgpa === null) {
    fieldErrors.value.cgpa = ['Your current CGPA is required for eligibility assessment.']
    isValid = false
  } else if (isNaN(form.value.cgpa) || form.value.cgpa < 0 || form.value.cgpa > 10) {
    fieldErrors.value.cgpa = ['Please enter a valid CGPA between 0 and 10.']
    isValid = false
  }

  if (!form.value.graduationYear) {
    fieldErrors.value.graduationYear = ['Please indicate your expected year of graduation.']
    isValid = false
  }

  if (form.value.activeBacklog === '' || form.value.activeBacklog === null) {
    fieldErrors.value.activeBacklog = ['Please correctly specify your active backlog count.']
    isValid = false
  } else if (isNaN(form.value.activeBacklog) || form.value.activeBacklog < 0) {
    fieldErrors.value.activeBacklog = ['Active backlog count must be 0 or greater.']
    isValid = false
  }

  if (!isValid) {
    toast.error('Please correct the highlighted fields.')
    return
  }

  isLoading.value = true

  try {
    const formData = new FormData()
    formData.append('email', form.value.email)
    formData.append('password', form.value.password)
    formData.append('confirm_password', form.value.confirmPassword)
    formData.append('name', form.value.name)
    formData.append('usn', form.value.usn)
    formData.append('branch', form.value.branch)
    formData.append('cgpa', form.value.cgpa)
    formData.append('graduation_year', form.value.graduationYear)
    formData.append('backlog_history', form.value.backlogHistory)
    formData.append('active_backlog', form.value.activeBacklog)
    formData.append('skills', form.value.skills)
    if(form.value.resume) {
      formData.append('resume', form.value.resume)
    }

    const data = await apiFetch('/auth/register/student', {
      method: 'POST',
      body: formData
    })

    setAuth(data.access_token, data.role, data.user_id)
    toast.success('Registration successful! Redirecting...')
    
    setTimeout(() => {
      router.push('/student/home')
    }, 2500)
  } catch (error) {
    if (error.validationErrors) {
      if (error.validationErrors.email) fieldErrors.value.email = error.validationErrors.email
      if (error.validationErrors.password) fieldErrors.value.password = error.validationErrors.password
      if (error.validationErrors.confirm_password) fieldErrors.value.confirmPassword = error.validationErrors.confirm_password
      if (error.validationErrors.name) fieldErrors.value.name = error.validationErrors.name
      if (error.validationErrors.usn) fieldErrors.value.usn = error.validationErrors.usn
      if (error.validationErrors.branch) fieldErrors.value.branch = error.validationErrors.branch
      if (error.validationErrors.cgpa) fieldErrors.value.cgpa = error.validationErrors.cgpa
      if (error.validationErrors.graduation_year) fieldErrors.value.graduationYear = error.validationErrors.graduation_year
      if (error.validationErrors.backlog_history) fieldErrors.value.backlogHistory = error.validationErrors.backlog_history
      if (error.validationErrors.active_backlog) fieldErrors.value.activeBacklog = error.validationErrors.active_backlog
      if (error.validationErrors.skills) fieldErrors.value.skills = error.validationErrors.skills
      if (error.validationErrors.resume) fieldErrors.value.resume = error.validationErrors.resume
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
