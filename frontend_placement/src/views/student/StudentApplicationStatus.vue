<template>
  <div class="container mt-4 d-flex justify-content-center">
    <div v-if="isLoading" class="text-center mt-5">Loading Application...</div>
    <div v-else-if="app" class="card shadow-sm border-0" style="width: 80%;">
      <div class="card-body p-5">
        <div class="d-flex justify-content-between align-items-center mb-4">
          <h4 class="fw-semibold m-0">Application: {{ app.company_name }} - {{ app.drive_title }}</h4>
          <router-link to="/student/home" class="btn btn-outline-secondary btn-sm">Back to Dashboard</router-link>
        </div>

        <div class="row mb-4">
          <div class="col-md-3 fw-semibold text-muted">Applied Date</div>
          <div class="col-md-9">{{ new Date(app.applied_date).toLocaleDateString() }}</div>
        </div>

        <div class="row mb-4">
          <div class="col-md-3 fw-semibold text-muted">Current Status</div>
          <div class="col-md-9">
            <span class="badge fs-6" :class="{
              'bg-success': app.status === 'Selected',
              'bg-danger': app.status === 'Rejected',
              'bg-secondary': app.status === 'Applied' || app.status === 'Withdrawn',
              'bg-dark': app.status === 'In Progress'
            }">
              {{ app.status }}
            </span>
          </div>
        </div>

        <div class="row mb-4">
          <div class="col-md-3 fw-semibold text-muted">Resume Used</div>
          <div class="col-md-9">
            <a v-if="app.resume_filename" :href="`${BASE_URL}/files/resume/${app.resume_filename}?token=${authState.token}`" target="_blank" class="btn btn-outline-dark btn-sm">
              View Resume
            </a>
            <span v-else class="text-muted">Default Profile Resume</span>
          </div>
        </div>

        <h5 class="fw-semibold mt-5 mb-3 border-bottom pb-2">Round Progress</h5>
        <div v-if="app.rounds && app.rounds.length > 0" class="table-responsive">
          <table class="table table-bordered">
            <thead class="table-light">
              <tr>
                <th>Round</th>
                <th>Name</th>
                <th>Scheduled Date</th>
                <th>Status</th>
                <th>Result Date</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(roundName, index) in app.rounds" :key="index" :class="{'table-active': index === app.current_round_index}">
                <td>{{ index + 1 }}</td>
                <td>{{ roundName }}</td>
                <td>{{ app.round_dates[index] }}</td>
                <td>
                  <span class="badge" :class="{
                    'bg-success': app.round_statuses[index] === 'Cleared' || app.round_statuses[index] === 'Selected',
                    'bg-danger': app.round_statuses[index] === 'Rejected',
                    'bg-warning text-dark': app.round_statuses[index] === 'Pending'
                  }">
                    {{ app.round_statuses[index] || 'Pending' }}
                  </span>
                </td>
                <td>{{ app.round_result_dates[index] || '-' }}</td>
              </tr>
            </tbody>
          </table>
        </div>
        <div v-else class="text-muted">No rounds specified.</div>

        <hr class="my-5" />

        <div v-if="errorMessages.length > 0" class="alert alert-danger py-2 mb-4 text-start">
          <ul class="mb-0 ps-3">
            <li v-for="(msg, index) in errorMessages" :key="index">{{ msg }}</li>
          </ul>
        </div>

        <div v-if="successMessage" class="alert alert-success py-2 mb-4 text-center">
          {{ successMessage }}
        </div>

        <div class="text-center" v-if="app.drive_status === 'Open'">
          <p class="text-muted mb-2">No longer interested in this drive?</p>
          <button class="btn btn-outline-danger" @click="handleWithdraw" :disabled="isWithdrawing || app.status === 'Withdrawn'">
            {{ isWithdrawing ? 'Withdrawing...' : 'Withdraw Application' }}
          </button>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup>
import { BASE_URL } from '../../composables/useApi'
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useApi } from '../../composables/useApi'
import { useModal } from '../../composables/useModal'
import { authState } from '../../store/auth'

const route = useRoute()
const router = useRouter()
const { apiFetch } = useApi()
const { confirm } = useModal()

const app = ref(null)
const isLoading = ref(true)
const isWithdrawing = ref(false)
const errorMessages = ref([])
const successMessage = ref('')

onMounted(async () => {
  try {
    const data = await apiFetch(`/student/applications/${route.params.id}`)
    app.value = data
  } catch (error) {
    errorMessages.value.push(error.message || 'Failed to load application details.')
  } finally {
    isLoading.value = false
  }
})

const handleWithdraw = async () => {
  const isConfirmed = await confirm("Are you sure you want to withdraw this application? This cannot be undone.")
  if (!isConfirmed) return

  isWithdrawing.value = true
  errorMessages.value = []
  successMessage.value = ''

  try {
    await apiFetch(`/student/applications/${route.params.id}`, {
      method: 'DELETE'
    })

    successMessage.value = 'Application withdrawn successfully. Redirecting...'
    setTimeout(() => {
      router.push('/student/home')
    }, 1500)
  } catch (error) {
    errorMessages.value.push(error.message || 'Failed to withdraw application.')
  } finally {
    isWithdrawing.value = false
  }
}
</script>

<style scoped>
</style>
