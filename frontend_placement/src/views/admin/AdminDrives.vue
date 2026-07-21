<template>
  <div class="container mt-4 mb-5">
    
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h4 class="fw-bold mb-1 text-dark">Manage Job Drives</h4>
        <p class="text-muted mb-0">Approve or reject placement drive postings from companies.</p>
      </div>
      
      <!-- Search -->
      <form @submit.prevent="fetchDrives" class="d-flex">
        <input type="text" class="form-control me-2" placeholder="Search by title..." v-model="searchQuery">
        <button type="submit" class="btn btn-outline-dark">Search</button>
      </form>
    </div>

    <!-- Error Display -->
    <div v-if="error" class="alert alert-danger mb-4">
      {{ error }}
    </div>

    <!-- Success Display -->
    <div v-if="actionSuccess" class="alert alert-success mb-4">
      {{ actionSuccess }}
    </div>

    <!-- Tabs Navigation -->
    <ul class="nav nav-pills mb-4 gap-2">
      <li class="nav-item">
        <button class="nav-link" :class="{ active: activeTab === 'pending' }" @click="activeTab = 'pending'">Pending Approval</button>
      </li>
      <li class="nav-item">
        <button class="nav-link" :class="{ active: activeTab === 'approved' }" @click="activeTab = 'approved'">Approved Drives</button>
      </li>
    </ul>

    <!-- Loading State -->
    <div v-if="isLoading" class="text-center mt-5">
      <div class="spinner-border text-dark" role="status"></div>
    </div>
    
    <!-- Tab Content -->
    <div v-else class="tab-content">
      
      <!-- PENDING TAB -->
      <div v-if="activeTab === 'pending'">
        <div v-if="data.pending_drives.length === 0" class="text-muted text-center py-5 bg-white rounded shadow-sm">
          No job drives pending approval.
        </div>
        <div v-else class="row g-3">
          <div v-for="drive in data.pending_drives" :key="drive.id" class="col-md-6">
            <div class="card border-0 shadow-sm h-100 hover-card">
              <div class="card-body p-4">
                <div class="d-flex justify-content-between align-items-start mb-3">
                  <div>
                    <h5 class="fw-bold mb-1">{{ drive.title }}</h5>
                    <div class="text-dark fw-medium small">{{ drive.company_name }}</div>
                  </div>
                </div>
                
                <div class="d-flex gap-2">
                  <button @click="viewDriveDetails(drive.id)" class="btn btn-outline-dark btn-sm flex-fill">View Details</button>
                  <button @click="handleAction('approve', drive.id)" class="btn btn-success btn-sm flex-fill" :disabled="isActioning">Approve</button>
                  <button @click="handleAction('reject', drive.id)" class="btn btn-danger btn-sm flex-fill" :disabled="isActioning">Reject</button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- APPROVED TAB -->
      <div v-if="activeTab === 'approved'">
        <div v-if="data.approved_drives.length === 0" class="text-muted text-center py-5 bg-white rounded shadow-sm">
          No approved drives found.
        </div>
        <div v-else class="row g-3">
          <div v-for="drive in data.approved_drives" :key="drive.id" class="col-md-6">
            <div class="card border-0 shadow-sm h-100 hover-card">
              <div class="card-body p-4">
                <div class="d-flex justify-content-between align-items-start mb-3">
                  <div>
                    <h5 class="fw-bold mb-1">{{ drive.title }}</h5>
                    <div class="text-dark fw-medium small">{{ drive.company_name }}</div>
                  </div>
                </div>
                
                <div class="d-flex gap-2">
                  <button @click="viewDriveDetails(drive.id)" class="btn btn-outline-dark btn-sm flex-fill">View Details</button>
                  <a v-if="drive.jd_filename" :href="`http://localhost:5000/api/files/jd/${drive.jd_filename}?token=${authState.token}`" target="_blank" class="btn btn-outline-secondary btn-sm flex-fill">View JD</a>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

    </div>

    <!-- View Drive Modal -->
    <div class="modal fade" id="driveDetailModal" tabindex="-1" aria-hidden="true">
      <div class="modal-dialog modal-dialog-centered modal-lg">
        <div class="modal-content border-0 shadow">
          <div class="modal-header bg-dark text-white border-bottom-0 pb-3">
            <h5 class="modal-title fw-bold">Drive Details</h5>
            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          
          <div class="modal-body p-0">
            <div v-if="isLoadingDetails" class="text-center py-5">
              <div class="spinner-border text-dark" role="status"></div>
            </div>
            
            <div v-else-if="selectedDrive" class="p-4">
              <!-- Header -->
              <div class="d-flex justify-content-between align-items-start mb-4">
                <div>
                  <h4 class="fw-bold mb-1">{{ selectedDrive.title }}</h4>
                  <div class="text-dark fw-medium">{{ selectedDrive.company_name }}</div>
                </div>
                <div>
                  <a v-if="selectedDrive.jd_filename" :href="`http://localhost:5000/api/files/jd/${selectedDrive.jd_filename}?token=${authState.token}`" target="_blank" class="btn btn-outline-secondary btn-sm me-2">View JD Document</a>
                </div>
              </div>

              <!-- Eligibility Criteria -->
              <div class="row g-3 mb-4 bg-light p-3 rounded">
                <h6 class="fw-bold text-dark w-100 mb-2 border-bottom pb-2">Eligibility Criteria</h6>
                
                <div class="col-sm-4">
                  <div class="small text-muted fw-semibold text-uppercase">CTC</div>
                  <div class="fw-medium text-dark">{{ selectedDrive.ctc }} LPA</div>
                </div>
                <div class="col-sm-4">
                  <div class="small text-muted fw-semibold text-uppercase">Min CGPA</div>
                  <div class="fw-medium text-dark">{{ selectedDrive.min_cgpa }}</div>
                </div>
                <div class="col-sm-4">
                  <div class="small text-muted fw-semibold text-uppercase">Deadline</div>
                  <div class="fw-medium text-dark">{{ selectedDrive.deadline }}</div>
                </div>
                <div class="col-sm-4">
                  <div class="small text-muted fw-semibold text-uppercase">Branches</div>
                  <div class="fw-medium text-dark">{{ selectedDrive.allowed_branches.join(', ') }}</div>
                </div>
                <div class="col-sm-4">
                  <div class="small text-muted fw-semibold text-uppercase">Grad Years</div>
                  <div class="fw-medium text-dark">{{ selectedDrive.allowed_grad_years.join(', ') }}</div>
                </div>
                <div class="col-sm-4">
                  <div class="small text-muted fw-semibold text-uppercase">Required Skills</div>
                  <div class="fw-medium text-dark">{{ selectedDrive.skills_required || 'None' }}</div>
                </div>
                <div class="col-sm-6">
                  <div class="small text-muted fw-semibold text-uppercase">Backlog History Allowed</div>
                  <div class="fw-medium text-dark">{{ selectedDrive.history_backlog_allowed }}</div>
                </div>
                <div class="col-sm-6">
                  <div class="small text-muted fw-semibold text-uppercase">Active Backlogs Allowed</div>
                  <div class="fw-medium text-dark">{{ selectedDrive.allowed_active_backlogs }}</div>
                </div>
              </div>

              <!-- Interview Rounds -->
              <h6 class="fw-bold mb-3 border-bottom pb-2">Interview Rounds</h6>
              <div v-if="selectedDrive.rounds && selectedDrive.rounds.length > 0" class="mb-4">
                <div v-for="(round, index) in selectedDrive.rounds" :key="index" class="d-flex justify-content-between mb-2">
                  <span class="fw-medium text-dark">{{ index + 1 }}. {{ round }}</span>
                  <span class="text-muted small">{{ selectedDrive.round_dates[index] }}</span>
                </div>
              </div>
              <div v-else class="text-muted small mb-4">No rounds defined.</div>
              
              <!-- Action Buttons in Modal (Only if Pending) -->
              <div v-if="selectedDrive.approval_status === 'Pending'" class="d-flex gap-2 justify-content-end mt-4 pt-3 border-top">
                <button @click="handleActionModal('approve', selectedDrive.id)" class="btn btn-success px-4" :disabled="isActioning">Approve Drive</button>
                <button @click="handleActionModal('reject', selectedDrive.id)" class="btn btn-danger px-4" :disabled="isActioning">Reject Drive</button>
              </div>

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
import { useModal } from '../../composables/useModal'
import { authState } from '../../store/auth'

const { apiFetch } = useApi()
const { confirm } = useModal()

const isLoading = ref(true)
const isActioning = ref(false)
const isLoadingDetails = ref(false)
const error = ref('')
const actionSuccess = ref('')
const activeTab = ref('pending')
const searchQuery = ref('')
const selectedDrive = ref(null)

const data = ref({
  pending_drives: [],
  approved_drives: []
})

const fetchDrives = async () => {
  try {
    isLoading.value = true
    error.value = ''
    
    let url = '/admin/drives'
    if (searchQuery.value) {
      url += `?search=${encodeURIComponent(searchQuery.value)}`
    }

    const response = await apiFetch(url)
    data.value = response
    
    if (response.pending_drives.length === 0 && response.approved_drives.length > 0 && !searchQuery.value) {
      activeTab.value = 'approved'
    }
  } catch (err) {
    error.value = err.message || 'Failed to fetch drives'
  } finally {
    isLoading.value = false
  }
}

const handleAction = async (action, driveId) => {
  if (action === 'reject') {
    const isConfirmed = await confirm('Are you sure you want to reject this placement drive?')
    if (!isConfirmed) return
  }

  isActioning.value = true
  error.value = ''
  actionSuccess.value = ''
  try {
    const res = await apiFetch(`/admin/drives/${driveId}/${action}`, { method: 'PUT' })
    actionSuccess.value = res.message || `Drive ${action}ed successfully.`
    await fetchDrives()
  } catch (err) {
    error.value = err.message || `Failed to ${action} drive`
  } finally {
    isActioning.value = false
    setTimeout(() => { actionSuccess.value = ''; error.value = '' }, 3000)
  }
}

const handleActionModal = async (action, driveId) => {
  await handleAction(action, driveId)
  // Hide modal
  const modalEl = document.getElementById('driveDetailModal')
  const modal = window.bootstrap.Modal.getInstance(modalEl)
  if (modal) modal.hide()
}

const viewDriveDetails = async (driveId) => {
  // Show modal
  const modal = new window.bootstrap.Modal(document.getElementById('driveDetailModal'))
  modal.show()
  
  isLoadingDetails.value = true
  selectedDrive.value = null

  try {
    const res = await apiFetch(`/admin/drives/${driveId}`)
    selectedDrive.value = {
      ...res.drive,
      rounds: res.rounds,
      round_dates: res.round_dates,
      jd_filename: res.jd_filename,
      applicant_label: res.applicant_label,
      applications: res.applications
    }
  } catch (err) {
    error.value = err.message || 'Failed to fetch drive details'
    modal.hide()
  } finally {
    isLoadingDetails.value = false
  }
}

onMounted(() => {
  fetchDrives()
})
</script>

<style scoped>
.hover-card {
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.hover-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 .5rem 1rem rgba(0,0,0,.15)!important;
}
.nav-pills .nav-link {
  color: #495057;
  cursor: pointer;
  border-radius: 50rem;
  padding: 0.5rem 1.25rem;
}
.nav-pills .nav-link.active {
  background-color: #212529;
  color: #fff;
}
.nav-pills .nav-link:hover:not(.active) {
  background-color: #e9ecef;
}
</style>
