<template>
  <div class="container">
    
    <div v-if="isLoading">
      <!-- Top bar skeleton -->
      <div class="row mb-4">
        <div class="col-md-12 d-flex justify-content-end gap-2">
          <div class="skeleton-box skeleton-button"></div>
          <div class="skeleton-box skeleton-button"></div>
        </div>
      </div>
      
      <!-- Stats skeleton -->
      <div class="row g-4 mb-4">
        <div class="col-md-4" v-for="i in 3" :key="i">
          <div class="card h-100 text-center shadow-sm border-0 p-4">
            <div class="skeleton-box skeleton-title mx-auto mb-3" style="width: 50%;"></div>
            <div class="skeleton-box skeleton-text mx-auto" style="width: 40%; height: 32px;"></div>
          </div>
        </div>
      </div>
      
      <!-- Tabs skeleton -->
      <ul class="nav nav-tabs justify-content-center mb-4">
        <li class="nav-item px-2" v-for="i in 3" :key="i">
          <div class="skeleton-box skeleton-button" style="height: 40px;"></div>
        </li>
      </ul>
      
      <!-- List skeleton -->
      <div class="d-flex flex-column align-items-center mt-4">
        <div class="card border-0 mb-3 shadow-sm w-100 p-3" style="max-width: 80%;" v-for="i in 3" :key="i">
          <div class="row align-items-center">
            <div class="col-md-3"><div class="skeleton-box skeleton-text w-75"></div></div>
            <div class="col-md-3"><div class="skeleton-box skeleton-text w-100"></div></div>
            <div class="col-md-2"><div class="skeleton-box skeleton-text w-50"></div></div>
            <div class="col-md-2"><div class="skeleton-box skeleton-text w-75"></div></div>
            <div class="col-md-2 text-md-end"><div class="skeleton-box skeleton-button w-100" style="height: 31px;"></div></div>
          </div>
        </div>
      </div>
    </div>

    <div v-else>

      <div class="row mb-4 align-items-center">
        <div class="col-md-12 d-flex justify-content-end align-items-center gap-3">
          <select v-if="resumes.length > 1 && sortByMatchScore" v-model="selectedResumeId" @change="fetchData" class="form-select shadow-sm" style="width: auto;">
            <option value="">Default Profile Skills</option>
            <option v-for="res in resumes" :key="res.id" :value="res.id">{{ res.name }}</option>
          </select>
          <button @click="toggleAISort" class="btn btn-dark shadow d-flex justify-content-center align-items-center" style="width: 42px; height: 42px;" :class="{'active': sortByMatchScore}" title="Sort based on resume-jd match">
            <i class="bi bi-funnel fs-8"></i>
          </button>
        </div>
      </div>

      <div v-if="sortByMatchScore" class="alert alert-info py-2 small d-flex align-items-center gap-2 mb-4 shadow-sm" role="alert" style="width: 80%; margin: 0 auto;">
        <i class="bi bi-info-circle-fill"></i>
        Jobs are currently sorted by automatically matching chosen resume's skills against the Job Description.
      </div>

      <!-- Tabs for jobs -->
      <ul class="nav nav-tabs justify-content-center" role="tablist">
        <li class="nav-item">
          <button class="nav-link active" data-bs-toggle="tab" data-bs-target="#new-applications">
            New Applications
          </button>
        </li>
        <li class="nav-item">
          <button class="nav-link" data-bs-toggle="tab" data-bs-target="#my-applications">
            My Applications
          </button>
        </li>
        <li class="nav-item">
          <button class="nav-link" data-bs-toggle="tab" data-bs-target="#ineligible-jobs">
            Ineligible Jobs
          </button>
        </li>
      </ul>

      <div class="tab-content mt-4">
        <!-- New Applications -->
        <div class="tab-pane fade show active" id="new-applications">
          <div class="d-flex flex-column align-items-center">
            <div v-for="drive in eligibleDrives" :key="drive.id" class="card border-dark mb-3 shadow-sm" style="width: 80%;">
              <div class="card-body">
                <div v-if="sortByMatchScore && drive.match_score !== undefined" class="d-flex justify-content-end mb-2">
                  <span class="badge bg-success shadow-sm" style="border-radius: 20px; padding: 0.5em 0.8em; font-size: 0.85rem;" title="AI Match Score">
                    <i class="bi bi-stars"></i> {{ drive.match_score }}% Match
                  </span>
                </div>
                <div class="row align-items-center text-center text-md-start">
                  <div class="col-md-3 fw-bold">{{ drive.company_name }}</div>
                  <div class="col-md-3">{{ drive.title }}</div>
                  <div class="col-md-2">₹{{ drive.ctc }} LPA</div>
                  <div class="col-md-2 text-muted small">Ends: {{ drive.deadline }}</div>
                  <div class="col-md-2 text-md-end mt-2 mt-md-0">
                    <router-link :to="`/student/job/${drive.id}`" class="btn btn-dark btn-sm w-100">View Details</router-link>
                  </div>
                </div>
              </div>
            </div>
            <div v-if="eligibleDrives.length === 0" class="text-muted mt-4">No new placement drives available.</div>
          </div>
        </div>

        <!-- My Applications -->
        <div class="tab-pane fade" id="my-applications">
          <div class="d-flex flex-column align-items-center">
            <div v-for="app in applications" :key="app.id" class="card border-secondary mb-3 shadow-sm" style="width: 80%;">
              <div class="card-body">
                <div v-if="sortByMatchScore && app.match_score !== undefined" class="d-flex justify-content-end mb-2">
                  <span class="badge bg-success shadow-sm" style="border-radius: 20px; padding: 0.5em 0.8em; font-size: 0.85rem;" title="AI Match Score">
                    <i class="bi bi-stars"></i> {{ app.match_score }}% Match
                  </span>
                </div>
                <div class="row align-items-center text-center text-md-start">
                  <div class="col-md-3 fw-bold">{{ app.company_name }}</div>
                  <div class="col-md-3">{{ app.drive_title }}</div>
                  <div class="col-md-4">
                    <span class="badge bg-secondary">{{ app.status }}</span>
                  </div>
                  <div class="col-md-2 text-md-end mt-2 mt-md-0">
                    <router-link :to="`/student/application/${app.id}`" class="btn btn-dark btn-sm w-100">View Status</router-link>
                  </div>
                </div>
              </div>
            </div>
            <div v-if="applications.length === 0" class="text-muted mt-4">You haven't applied to any jobs yet.</div>
          </div>
        </div>

        <!-- Ineligible Jobs -->
        <div class="tab-pane fade" id="ineligible-jobs">
          <div class="d-flex flex-column align-items-center">
            <div v-for="drive in ineligibleDrives" :key="drive.id" class="card border-danger mb-3 shadow-sm" style="width: 80%;">
              <div class="card-body">
                <div v-if="sortByMatchScore && drive.match_score !== undefined" class="d-flex justify-content-end mb-2">
                  <span class="badge bg-success shadow-sm" style="border-radius: 20px; padding: 0.5em 0.8em; font-size: 0.85rem;" title="AI Match Score">
                    <i class="bi bi-stars"></i> {{ drive.match_score }}% Match
                  </span>
                </div>
                <div class="row align-items-center text-center text-md-start">
                  <div class="col-md-3 fw-bold">{{ drive.company_name }}</div>
                  <div class="col-md-3">{{ drive.title }}</div>
                  <div class="col-md-2">₹{{ drive.ctc }} LPA</div>
                  <div class="col-md-2 text-danger small">Ineligible</div>
                  <div class="col-md-2 text-md-end mt-2 mt-md-0">
                    <router-link :to="`/student/job/${drive.id}`" class="btn btn-outline-dark btn-sm w-100">View Details</router-link>
                  </div>
                </div>
              </div>
            </div>
            <div v-if="ineligibleDrives.length === 0" class="text-muted mt-4">No ineligible jobs.</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick } from 'vue'
import { useApi } from '../../composables/useApi'
import Chart from 'chart.js/auto'

const { apiFetch } = useApi()

const isLoading   = ref(true)
const isExporting = ref(false)
const searchQuery = ref('')
const sortByMatchScore = ref(false)
const resumes = ref([])
const selectedResumeId = ref('')
const eligibleDrives    = ref([])
const ineligibleDrives  = ref([])
const applications      = ref([])
const appsTotal         = ref(0)
const statusCounts      = ref({})

const exportBanner = reactive({
  show:    false,
  type:    'alert-success',
  title:   '',
  message: ''
})

let statusChartInstance = null

const fetchData = async () => {
  try {
    isLoading.value = true
    if (resumes.value.length === 0) {
      try {
        resumes.value = await apiFetch('/student/resumes')
        if (resumes.value.length === 1) {
          selectedResumeId.value = resumes.value[0].id
        }
      } catch (e) {
        console.error("Failed to load resumes:", e)
      }
    }

    let jobsUrl = '/student/jobs'
    let appsUrl = '/student/applications'
    
    let params = []
    if (searchQuery.value) {
      params.push(`search=${encodeURIComponent(searchQuery.value)}`)
    }
    if (sortByMatchScore.value) {
      params.push('sort_by=match_score')
      if (selectedResumeId.value) {
        params.push(`resume_id=${selectedResumeId.value}`)
      }
    }
    
    if (params.length > 0) {
      const q = '?' + params.join('&')
      jobsUrl += q
    }
    
    let appParams = []
    if (searchQuery.value) {
      appParams.push(`search=${encodeURIComponent(searchQuery.value)}`)
    }
    if (sortByMatchScore.value) {
      appParams.push('sort_by=match_score')
      if (selectedResumeId.value) {
        appParams.push(`resume_id=${selectedResumeId.value}`)
      }
    }
    
    if (appParams.length > 0) {
      appsUrl += '?' + appParams.join('&')
    }

    const [jobsData, appsData] = await Promise.all([
      apiFetch(jobsUrl),
      apiFetch(appsUrl)
    ])
    
    eligibleDrives.value = jobsData.eligible_drives
    ineligibleDrives.value = jobsData.ineligible_drives
    
    applications.value = appsData.applications
    appsTotal.value = appsData.total
    statusCounts.value = appsData.status_counts

    await nextTick()
    renderChart()
  } catch (err) {
    console.error("Failed to load dashboard data:", err)
  } finally {
    isLoading.value = false
  }
}

const toggleAISort = () => {
  sortByMatchScore.value = !sortByMatchScore.value
  fetchData()
}

const renderChart = () => {
  if (appsTotal.value > 0) {
    const ctxStatus = document.getElementById('statusPieChart')
    if (ctxStatus) {
      if (statusChartInstance) statusChartInstance.destroy()
      
      const labels = Object.keys(statusCounts.value)
      const values = Object.values(statusCounts.value)
      
      const colorMap = {
        'Selected': '#198754',
        'Rejected': '#dc3545',
        'In Progress': '#ffc107',
        'Applied': '#6c757d',
        'Pending': '#6c757d'
      }
      const bgColors = labels.map(l => colorMap[l] || '#0d6efd')

      statusChartInstance = new Chart(ctxStatus, {
        type: 'doughnut',
        data: {
          labels: labels,
          datasets: [{
            data: values,
            backgroundColor: bgColors,
            borderWidth: 2,
            hoverOffset: 4
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { 
            legend: { position: 'right' }
          },
          cutout: '70%'
        }
      })
    }
  }
}

onMounted(() => {
  fetchData()
})

const exportCsv = async () => {
  isExporting.value = true
  exportBanner.show = false

  try {
    await apiFetch('/student/export_csv', { method: 'POST' })
    exportBanner.type    = 'alert-success'
    exportBanner.title   = 'Export started!'
    exportBanner.message = 'Your CSV is being generated. Check your registered email — it will arrive shortly as an attachment.'
  } catch (err) {
    exportBanner.type    = 'alert-danger'
    exportBanner.title   = 'Export failed.'
    exportBanner.message = err?.message || 'Something went wrong. Please try again.'
  } finally {
    isExporting.value = false
    exportBanner.show = true
    // Auto-dismiss after 8 seconds
    setTimeout(() => { exportBanner.show = false }, 8000)
  }
}
</script>

<style scoped>
</style>
