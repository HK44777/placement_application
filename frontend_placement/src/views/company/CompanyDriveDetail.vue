<template>
  <div class="container mt-4 mb-5">
    <div v-if="isLoading" class="text-center mt-5">
      <div class="spinner-border text-dark" role="status"></div>
    </div>
    
    <div v-else-if="error" class="alert alert-danger text-center">
      {{ error }}
    </div>

    <div v-else>
      
      <!-- Action Alerts -->
      <div v-if="actionError" class="alert alert-danger text-center mb-4">
        {{ actionError }}
      </div>
      <div v-if="actionSuccess" class="alert alert-success text-center mb-4">
        {{ actionSuccess }}
      </div>

      <!-- Drive Header -->
      <div class="card shadow-sm border-0 mb-4">
        <div class="card-body p-4 d-flex justify-content-between align-items-start">
          <div>
            <h4 class="fw-bold mb-1 text-dark">{{ drive.title }}</h4>
            <div class="d-flex align-items-center gap-3 text-muted small mt-2">
              <span><i class="bi bi-cash me-1"></i> {{ drive.ctc }} LPA</span>
              <span><i class="bi bi-calendar-event me-1"></i> Deadline: {{ drive.deadline }}</span>
              <span>
                <span class="badge" :class="drive.status === 'Open' ? 'bg-success' : 'bg-secondary'">
                  {{ drive.status }}
                </span>
              </span>
            </div>
          </div>
          <div>
            <a v-if="drive.jd_filename" :href="`${BASE_URL}/files/jd/${drive.jd_filename}?token=${authState.token}`" target="_blank" class="btn btn-outline-secondary btn-sm me-2">View JD</a>
            
            <button v-if="drive.status === 'Open'" @click="closeDrive" class="btn btn-danger btn-sm" :disabled="isClosing">
              {{ isClosing ? 'Closing...' : 'Close Drive Now' }}
            </button>
          </div>
        </div>
      </div>

      <!-- Detail Info -->
      <div class="row g-4 mb-4">
        <!-- Criteria -->
        <div class="col-md-6">
          <div class="card shadow-sm border-0 h-100">
            <div class="card-body p-4">
              <h6 class="fw-bold mb-3 text-dark">Eligibility Criteria</h6>
              <ul class="list-unstyled mb-0">
                <li class="mb-2"><span class="fw-medium text-muted">Min CGPA:</span> {{ drive.min_cgpa }}</li>
                <li class="mb-2"><span class="fw-medium text-muted">Branches:</span> {{ drive.allowed_branches.join(', ') }}</li>
                <li class="mb-2"><span class="fw-medium text-muted">Grad Years:</span> {{ drive.allowed_grad_years.join(', ') }}</li>
                <li class="mb-2"><span class="fw-medium text-muted">Backlog History Allowed:</span> {{ drive.history_backlog_allowed }}</li>
                <li><span class="fw-medium text-muted">Active Backlogs Allowed:</span> {{ drive.allowed_active_backlogs }}</li>
              </ul>
            </div>
          </div>
        </div>

        <!-- Rounds -->
        <div class="col-md-6">
          <div class="card shadow-sm border-0 h-100">
            <div class="card-body p-4">
              <h6 class="fw-bold mb-3 text-dark">Interview Rounds</h6>
              <div v-if="drive.rounds && drive.rounds.length > 0">
                <div v-for="(round, index) in drive.rounds" :key="index" class="d-flex justify-content-between border-bottom py-2">
                  <span class="fw-medium text-dark">{{ index + 1 }}. {{ round }}</span>
                  <span class="text-muted small">{{ drive.round_dates[index] }}</span>
                </div>
              </div>
              <div v-else class="text-muted small">No rounds defined.</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Applicant Section (If Open) -->
      <div v-if="drive.status === 'Open'" class="card shadow-sm border-0 text-center p-5">
        <h1 class="display-4 fw-bold text-dark mb-2">{{ drive.applicant_count || 0 }}</h1>
        <p class="text-muted mb-0 fw-medium">Students have applied so far</p>
        <p class="text-muted small mt-2">You can manage applicants once the drive is closed.</p>
      </div>

      <!-- Applicant Management Section (If Closed) -->
      <div v-if="drive.status === 'Closed'" class="card shadow-sm border-0">
        <div class="card-header bg-white border-bottom-0 pt-4 pb-2">
          <h5 class="fw-bold mb-0">Manage Applicants</h5>
        </div>
        <div class="card-body p-0">
          <div class="table-responsive">
            <table class="table table-hover align-middle mb-0">
              <thead class="table-light">
                <tr>
                  <th class="ps-4">Student</th>
                  <th>Branch / CGPA</th>
                  <th>Current Status</th>
                  <th class="text-end pe-4">Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-if="!drive.applications || drive.applications.length === 0">
                  <td colspan="4" class="text-center text-muted py-4">No applications received.</td>
                </tr>
                <tr v-for="app in drive.applications" :key="app.id">
                  <td class="ps-4">
                    <div class="fw-semibold text-dark">{{ app.student_name }}</div>
                    <div class="small text-muted">{{ app.student_usn }}</div>
                  </td>
                  <td>
                    <div>{{ app.student_branch }}</div>
                    <div class="small text-muted">CGPA: {{ app.student_cgpa }}</div>
                  </td>
                  <td>
                    <span class="badge" :class="{
                      'bg-success': app.status === 'Selected',
                      'bg-danger': app.status === 'Rejected',
                      'bg-warning text-dark': app.status === 'In Progress',
                      'bg-secondary': app.status === 'Applied'
                    }">
                      {{ app.status }}
                    </span>
                    <div class="small text-muted mt-1" style="font-size: 0.75rem;">
                      <span v-if="app.current_round_index < drive.rounds.length && app.status !== 'Selected' && app.status !== 'Rejected'">
                        Pending: {{ drive.rounds[app.current_round_index] }}
                      </span>
                    </div>
                  </td>
                  <td class="text-end pe-4">
                    <a v-if="app.resume_filename" :href="`${BASE_URL}/files/resume/${app.resume_filename}?token=${authState.token}`" target="_blank" class="btn btn-outline-secondary btn-sm me-2">Resume</a>
                    
                    <button v-if="app.status !== 'Selected' && app.status !== 'Rejected'" 
                            @click="openManageModal(app)" 
                            class="btn btn-dark btn-sm"
                            data-bs-toggle="modal" data-bs-target="#manageApplicantModal">
                      Manage
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- Manage Applicant Modal -->
      <div class="modal fade" id="manageApplicantModal" tabindex="-1" aria-hidden="true">
        <div class="modal-dialog modal-dialog-centered">
          <div class="modal-content border-0 shadow">
            <div class="modal-header border-bottom-0 pb-0">
              <h5 class="modal-title fw-bold">Update Applicant Status</h5>
              <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close" id="closeManageModal"></button>
            </div>
            
            <div v-if="selectedApp" class="modal-body">
              <div class="mb-4">
                <h6 class="fw-semibold text-dark mb-1">{{ selectedApp.student_name }} ({{ selectedApp.student_usn }})</h6>
                <div class="text-muted small">
                  Currently pending: <span class="fw-medium text-dark">{{ drive.rounds[selectedApp.current_round_index] }}</span>
                </div>
              </div>

              <div v-if="manageError" class="alert alert-danger small py-2">{{ manageError }}</div>

              <div class="d-grid gap-2">
                <!-- If there are more rounds, show 'Move to Next Round' -->
                <button v-if="selectedApp.current_round_index < drive.rounds.length - 1" 
                        @click="updateStatus('next_round')" 
                        class="btn btn-dark" :disabled="isUpdating">
                  <i class="bi bi-arrow-right-circle me-1"></i> Cleared (Move to Next Round)
                </button>
                
                <!-- Final Selection -->
                <button @click="updateStatus('select')" 
                        class="btn btn-success" :disabled="isUpdating">
                  <i class="bi bi-check-circle me-1"></i> Select (Final Offer)
                </button>

                <!-- Rejection -->
                <button @click="updateStatus('reject')" 
                        class="btn btn-danger" :disabled="isUpdating">
                  <i class="bi bi-x-circle me-1"></i> Reject
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { BASE_URL } from '../../composables/useApi'
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useApi } from '../../composables/useApi'
import { useModal } from '../../composables/useModal'
import { authState } from '../../store/auth'

const route = useRoute()
const { apiFetch } = useApi()
const { confirm } = useModal()
const driveId = route.params.id

const isLoading = ref(true)
const isClosing = ref(false)
const error = ref('')
const drive = ref(null)

const selectedApp = ref(null)
const isUpdating = ref(false)
const manageError = ref('')
const actionError = ref('')
const actionSuccess = ref('')

const fetchDrive = async () => {
  try {
    const data = await apiFetch(`/company/drives/${driveId}`)
    drive.value = data
  } catch (err) {
    error.value = err.message || 'Failed to fetch drive details'
  } finally {
    isLoading.value = false
  }
}

const closeDrive = async () => {
  const isConfirmed = await confirm('Are you sure you want to close this drive? Students will no longer be able to apply.')
  if (!isConfirmed) return
  
  isClosing.value = true
  actionError.value = ''
  actionSuccess.value = ''
  try {
    await apiFetch(`/company/drives/${driveId}/close`, { method: 'POST' })
    actionSuccess.value = 'Drive closed successfully.'
    await fetchDrive() // reload data to show applicant list
  } catch (err) {
    actionError.value = err.message || 'Failed to close drive'
  } finally {
    isClosing.value = false
    setTimeout(() => { actionSuccess.value = ''; actionError.value = '' }, 3000)
  }
}

const openManageModal = (app) => {
  selectedApp.value = app
  manageError.value = ''
}

const updateStatus = async (action) => {
  if (!selectedApp.value) return
  isUpdating.value = true
  manageError.value = ''

  try {
    await apiFetch(`/company/applications/${selectedApp.value.id}/status`, {
      method: 'PUT',
      body: JSON.stringify({ action })
    })
    
    // Close modal programmatically
    document.getElementById('closeManageModal').click()
    
    // Refresh applicant list
    actionSuccess.value = 'Applicant status updated successfully.'
    await fetchDrive()
  } catch (err) {
    manageError.value = err.message || 'Failed to update status'
  } finally {
    isUpdating.value = false
    setTimeout(() => { actionSuccess.value = ''; actionError.value = '' }, 3000)
  }
}

onMounted(() => {
  fetchDrive()
})
</script>
