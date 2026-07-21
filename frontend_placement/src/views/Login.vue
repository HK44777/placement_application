<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useApi } from '../composables/useApi'
import { useModal } from '../composables/useModal'
import { setAuth } from '../store/auth'
import { toast } from 'vue3-toastify'

const router = useRouter()
const { apiFetch } = useApi()
const { alert } = useModal()

const email = ref('')
const password = ref('')
const showPassword = ref(false)
const isLoading = ref(false)
const fieldErrors = ref({})
const globalError = ref('')
const registrationSuccess = ref(false)

onMounted(() => {
  if (history.state && history.state.companyRegistered) {
    registrationSuccess.value = true
    toast.info('Registration successful! Please wait for admin approval.')
    // Clear the state so it doesn't persist on page reload
    history.replaceState({ ...history.state, companyRegistered: false }, '')
  }
})

const validateForm = () => {
  fieldErrors.value = {}
  globalError.value = ''
  let isValid = true

  if (!email.value.trim()) {
    fieldErrors.value.email = ['Please provide your registered email address.']
    isValid = false
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.value)) {
    fieldErrors.value.email = ['Please enter a valid email address.']
    isValid = false
  }

  if (!password.value) {
    fieldErrors.value.password = ['Password is required to access your account.']
    isValid = false
  }

  return isValid
}

const handleLogin = async () => {
  if (!validateForm()) return

  isLoading.value = true
  
  try {
    const data = await apiFetch('/auth/login', {
      method: 'POST',
      body: JSON.stringify({
        email: email.value,
        password: password.value
      })
    })

    // Save auth token
    setAuth(data.access_token, data.role, data.user_id)
    toast.success('Login successful!')
    
    // Redirect based on role or status
    setTimeout(async () => {
      if (data.role === 'student') {
        router.push('/student/home')
      } else if (data.role === 'company') {
        if (data.approval_status === 'rejected') {
          await alert("Your company registration was rejected. Please update your profile.")
          router.push('/company/profile/edit')
        } else {
          router.push('/company/dashboard')
        }
      } else {
        router.push('/admin/dashboard')
      }
    }, 500)
  } catch (error) {
    // Show the specific error from the backend if it exists (e.g., "Your account is pending admin approval")
    // otherwise fallback to a generic invalid credentials message
    globalError.value = error.message || 'Invalid email or password.'
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <div class="d-flex align-items-center justify-content-center min-vh-100">
    <div class="card shadow-sm w-100" style="max-width: 420px;">
      <div class="card-body p-4">
        
        <router-link to="/" class="back-btn mb-3 d-inline-block">Home</router-link>
        
        <h4 class="text-center fw-semibold mb-4 text-dark">Login</h4>

        <form @submit.prevent="handleLogin" novalidate>
          <div v-if="globalError" class="alert alert-danger text-center small mb-3">{{ globalError }}</div>
          
          <div v-if="registrationSuccess" class="alert alert-success text-center small mb-3">
            Registration successful! Your profile has been sent to the admin for review. You will be able to log in once your account is approved.
          </div>

          <!-- Email -->
          <div class="mb-3">
            <div class="form-floating">
              <input type="email" class="form-control" :class="{'is-invalid': fieldErrors.email}" id="floatingEmail" placeholder="name@example.com" v-model="email" />
              <label for="floatingEmail" class="text-muted">Email address</label>
            </div>
            <div v-if="fieldErrors.email" class="d-block invalid-feedback">{{ fieldErrors.email[0] }}</div>
          </div>

          <!-- Password -->
          <div class="mb-4">
            <div class="input-group">
              <div class="form-floating flex-grow-1">
                <input :type="showPassword ? 'text' : 'password'" class="form-control" :class="{'is-invalid': fieldErrors.password}" id="floatingPassword" placeholder="Password" v-model="password" />
                <label for="floatingPassword" class="text-muted">Password</label>
              </div>
              <button type="button" class="input-group-text password-toggle-btn bg-white" :class="{'border-danger border-start-0': fieldErrors.password, 'border-start-0': !fieldErrors.password}" @click="showPassword = !showPassword" tabindex="-1">
                <svg v-if="!showPassword" xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" class="bi bi-eye-fill" viewBox="0 0 16 16">
                  <path d="M10.5 8a2.5 2.5 0 1 1-5 0 2.5 2.5 0 0 1 5 0"/>
                  <path d="M0 8s3-5.5 8-5.5S16 8 16 8s-3 5.5-8 5.5S0 8 0 8m8 3.5a3.5 3.5 0 1 0 0-7 3.5 3.5 0 0 0 0 7"/>
                </svg>
                <svg v-else xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" class="bi bi-eye-slash-fill" viewBox="0 0 16 16">
                  <path d="m10.79 12.912-1.614-1.615a3.5 3.5 0 0 1-4.474-4.474l-2.06-2.06C.938 6.278 0 8 0 8s3 5.5 8 5.5a7 7 0 0 0 2.79-.588M5.21 3.088A7 7 0 0 1 8 2.5c5 0 8 5.5 8 5.5s-.939 1.721-2.641 3.238l-2.09-2.09a3.5 3.5 0 0 0-4.474-4.474z"/>
                  <path d="M5.525 7.646a2.5 2.5 0 0 0 2.829 2.829zm4.95.708-2.829-2.83a2.5 2.5 0 0 1 2.829 2.829zm3.171 6-12-12 .708-.708 12 12z"/>
                </svg>
              </button>
            </div>
            <div v-if="fieldErrors.password" class="d-block invalid-feedback">{{ fieldErrors.password[0] }}</div>
          </div>

          <!-- Submit -->
          <div class="d-grid mb-4">
            <button type="submit" class="btn btn-primary" :disabled="isLoading">
              <span v-if="isLoading" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
              {{ isLoading ? 'Logging in...' : 'Login' }}
            </button>
          </div>
        </form>

        <!-- Register links -->
        <div class="text-center small">
          <p class="mb-2 text-muted">Don't have an account?</p>
          <router-link class="text-dark fw-bold text-decoration-none" to="/student-register">Register as Student</router-link>
          <span class="mx-2 text-muted">|</span>
          <router-link class="text-dark fw-bold text-decoration-none" to="/company-register">Register as Company</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
</style>
