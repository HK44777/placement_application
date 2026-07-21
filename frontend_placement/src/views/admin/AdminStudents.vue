<template>
  <div class="container mt-4 mb-5">
    
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h4 class="fw-bold mb-1 text-dark">Manage Students</h4>
        <p class="text-muted mb-0">View student profiles, application history, and manage access.</p>
      </div>
      
      <!-- Search -->
      <form @submit.prevent="fetchStudents" class="d-flex">
        <input type="text" class="form-control me-2" placeholder="Search by name or USN..." v-model="searchQuery">
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

    <!-- Loading State -->
    <div v-if="isLoading" class="text-center mt-5">
      <div class="spinner-border text-dark" role="status"></div>
    </div>
    
    <!-- Student List -->
    <div v-else>
      <div v-if="data.students.length === 0" class="text-muted text-center py-5 bg-white rounded shadow-sm border">
        No students found.
      </div>
      <div v-else class="card border-0 shadow-sm">
        <div class="table-responsive">
          <table class="table table-hover align-middle mb-0">
            <thead class="table-light">
              <tr>
                <th class="ps-4">Student Info</th>
                <th>Academic Info</th>
                <th>Status</th>
                <th class="text-end pe-4">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="student in data.students" :key="student.id" :class="{'opacity-75 bg-light': !student.is_active}">
                <td class="ps-4 py-3">
                  <div class="fw-bold text-dark">{{ student.name }}</div>
                  <div class="small text-muted">{{ student.usn }} | {{ student.email }}</div>
                </td>
                <td>
                  <div class="fw-medium">{{ student.branch }}</div>
                  <div class="small text-muted">CGPA: {{ student.cgpa }}</div>
                </td>
                <td>
                  <span v-if="student.is_active" class="badge bg-success">Active</span>
                  <span v-else class="badge bg-secondary">Deactivated</span>
                </td>
                <td class="text-end pe-4">
                  <button @click="viewStudentDetails(student.id)" class="btn btn-outline-dark btn-sm me-2">View</button>
                  <button v-if="student.is_active" @click="handleAction('deactivate', student.id)" class="btn btn-outline-danger btn-sm" :disabled="isActioning">Suspend</button>
                  <button v-else @click="handleAction('activate', student.id)" class="btn btn-success btn-sm" :disabled="isActioning">Activate</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- View Student Modal -->
    <div class="modal fade" id="studentDetailModal" tabindex="-1" aria-hidden="true">
      <div class="modal-dialog modal-dialog-centered modal-lg">
        <div class="modal-content border-0 shadow">
          <div class="modal-header bg-dark text-white border-bottom-0 pb-3">
            <h5 class="modal-title fw-bold">Student Profile & Applications</h5>
            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          
          <div class="modal-body p-0">
            <div v-if="isLoadingDetails" class="text-center py-5">
              <div class="spinner-border text-dark" role="status"></div>
            </div>
            
            <div v-else-if="selectedStudent" class="p-4">
              <!-- Profile Header -->
              <div class="d-flex justify-content-between align-items-start mb-4">
                <div>
                  <h4 class="fw-bold mb-1">{{ selectedStudent.student.name }}</h4>
                  <div class="text-muted">{{ selectedStudent.student.usn }} | {{ selectedStudent.student.email }}</div>
                </div>
                <div>
                  <a v-if="selectedStudent.student.resume_filename" :href="`${BASE_URL}/files/resume/${selectedStudent.student.resume_filename}?token=${authState.token}`" target="_blank" class="btn btn-outline-dark btn-sm">View Resume</a>
                </div>
              </div>

              <!-- Academic Details -->
              <div class="row g-3 mb-4 bg-light p-3 rounded">
                <div class="col-sm-4">
                  <div class="small text-muted fw-semibold text-uppercase">Branch</div>
                  <div class="fw-medium text-dark">{{ selectedStudent.student.branch }}</div>
                </div>
                <div class="col-sm-4">
                  <div class="small text-muted fw-semibold text-uppercase">CGPA</div>
                  <div class="fw-medium text-dark">{{ selectedStudent.student.cgpa }}</div>
                </div>
                <div class="col-sm-4">
                  <div class="small text-muted fw-semibold text-uppercase">Grad Year</div>
                  <div class="fw-medium text-dark">{{ selectedStudent.student.graduation_year }}</div>
                </div>
                <div class="col-sm-4">
                  <div class="small text-muted fw-semibold text-uppercase">Backlog History</div>
                  <div class="fw-medium text-dark">{{ selectedStudent.student.backlog_history }}</div>
                </div>
                <div class="col-sm-4">
                  <div class="small text-muted fw-semibold text-uppercase">Active Backlogs</div>
                  <div class="fw-medium text-dark">{{ selectedStudent.student.active_backlog }}</div>
                </div>
                <div class="col-sm-4">
                  <div class="small text-muted fw-semibold text-uppercase">Skills</div>
                  <div class="fw-medium text-dark">{{ selectedStudent.student.skills || 'N/A' }}</div>
                </div>
              </div>

              <!-- Application History -->
              <h6 class="fw-bold mb-3">Application History</h6>
              <div v-if="selectedStudent.applications.length === 0" class="text-muted small">
                No applications submitted yet.
              </div>
              <div v-else class="list-group">
                <div v-for="app in selectedStudent.applications" :key="app.id" class="list-group-item list-group-item-action border-0 shadow-sm mb-2 rounded">
                  <div class="d-flex w-100 justify-content-between">
                    <h6 class="mb-1 fw-bold">{{ app.drive_title }}</h6>
                    <small class="text-muted">{{ app.applied_date }}</small>
                  </div>
                  <p class="mb-1 small text-muted">{{ app.company_name }}</p>
                  <span class="badge" :class="{
                    'bg-success': app.status === 'Selected',
                    'bg-danger': app.status === 'Rejected',
                    'bg-warning text-dark': app.status === 'In Progress',
                    'bg-secondary': app.status === 'Applied'
                  }">
                    {{ app.status }}
                  </span>
                </div>
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
const searchQuery = ref('')
const selectedStudent = ref(null)

const data = ref({
  students: [],
  total: 0
})

const fetchStudents = async () => {
  try {
    isLoading.value = true
    error.value = ''
    
    let url = '/admin/students'
    if (searchQuery.value) {
      url += `?search=${encodeURIComponent(searchQuery.value)}`
    }

    const response = await apiFetch(url)
    data.value = response
  } catch (err) {
    error.value = err.message || 'Failed to fetch students'
  } finally {
    isLoading.value = false
  }
}

const handleAction = async (action, studentId) => {
  if (action === 'deactivate') {
    const isConfirmed = await confirm('Are you sure you want to deactivate this student? They will instantly lose access to the portal.')
    if (!isConfirmed) return
  }

  isActioning.value = true
  error.value = ''
  actionSuccess.value = ''
  try {
    const res = await apiFetch(`/admin/students/${studentId}/${action}`, { method: 'PUT' })
    actionSuccess.value = `Student ${action}d successfully.`
    await fetchStudents()
  } catch (err) {
    error.value = err.message || `Failed to ${action} student`
  } finally {
    isActioning.value = false
    setTimeout(() => { actionSuccess.value = ''; error.value = '' }, 3000)
  }
}

const viewStudentDetails = async (studentId) => {
  // Show modal
  const modal = new window.bootstrap.Modal(document.getElementById('studentDetailModal'))
  modal.show()
  
  isLoadingDetails.value = true
  selectedStudent.value = null

  try {
    const res = await apiFetch(`/admin/students/${studentId}`)
    selectedStudent.value = res
  } catch (err) {
    error.value = err.message || 'Failed to fetch student details'
    modal.hide()
  } finally {
    isLoadingDetails.value = false
  }
}

onMounted(() => {
  fetchStudents()
})
</script>
