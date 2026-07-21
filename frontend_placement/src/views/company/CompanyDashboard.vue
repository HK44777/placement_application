<template>
  <div class="container mt-4 mb-5">
    
    <!-- Error Display -->
    <div v-if="error" class="alert alert-danger mb-4">
      {{ error }}
    </div>

    <!-- Header Stats and Charts Skeletons -->
    <div v-if="isLoading" class="row g-4 mb-5">
      <div class="col-md-3">
        <div class="card h-100 text-center border-0 shadow-sm p-4">
          <div class="skeleton-box skeleton-text mx-auto mb-3" style="width: 70%;"></div>
          <div class="skeleton-box skeleton-title mx-auto mb-2" style="width: 50%; height: 48px;"></div>
          <div class="skeleton-box skeleton-text mx-auto mt-2" style="width: 40%;"></div>
        </div>
      </div>
      <div class="col-md-5">
        <div class="card h-100 border-0 shadow-sm p-4">
          <div class="skeleton-box skeleton-title mx-auto mb-4"></div>
          <div class="skeleton-box w-100" style="height: 200px;"></div>
        </div>
      </div>
      <div class="col-md-4">
        <div class="card h-100 border-0 shadow-sm p-4">
          <div class="skeleton-box skeleton-title mx-auto mb-4"></div>
          <div class="skeleton-box w-100 rounded-circle mx-auto" style="max-width: 200px; height: 200px;"></div>
        </div>
      </div>
    </div>

    <!-- Header Stats and Charts -->
    <div v-else class="row g-4 mb-5">
      
      <!-- Stat Card -->
      <div class="col-md-3">
        <div class="card h-100 text-center border-0 shadow-sm">
          <div class="card-body d-flex flex-column justify-content-center">
            <div class="text-muted small fw-semibold text-uppercase mb-2">Total Applications</div>
            <h1 class="display-5 fw-bold mb-0 text-dark">{{ data.total_applicants }}</h1>
            <div class="text-muted small mt-2">across all drives</div>
          </div>
        </div>
      </div>

      <!-- Chart 1: Applications per Drive -->
      <div class="col-md-5">
        <div class="card h-100 border-0 shadow-sm">
          <div class="card-body">
            <h6 class="fw-semibold text-center mb-3">Applications per Drive</h6>
            <div class="chart-container" style="position: relative; height: 260px; width: 100%;">
              <canvas v-if="data.chart_drives && data.chart_drives.length > 0" id="driveBarChart"></canvas>
              <div v-else class="text-center text-muted mt-5 pt-3">No approved or closed drives yet.</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Chart 2: Applicant Status Pie -->
      <div class="col-md-4">
        <div class="card h-100 border-0 shadow-sm">
          <div class="card-body">
            <h6 class="fw-semibold text-center mb-3">Applicant Status</h6>
            <div class="chart-container" style="position: relative; height: 260px; width: 100%;">
              <canvas v-if="data.total_applicants > 0" id="statusPieChart"></canvas>
              <div v-else class="text-center text-muted mt-5 pt-3">No applications yet.</div>
            </div>
          </div>
        </div>
      </div>

    </div>

    <!-- Main Drives Section -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h4 class="fw-bold mb-1 text-dark">My Job Drives</h4>
        <p class="text-muted mb-0">Manage your job postings and applications</p>
      </div>
      <router-link to="/company/drives/create" class="btn btn-dark px-4 fw-medium">Create Drive</router-link>
    </div>

    <!-- Tabs Navigation -->
    <ul class="nav nav-pills mb-4 gap-2">
      <li class="nav-item">
        <button class="nav-link" :class="{ active: activeTab === 'pending' }" @click="activeTab = 'pending'">Pending</button>
      </li>
      <li class="nav-item">
        <button class="nav-link" :class="{ active: activeTab === 'open' }" @click="activeTab = 'open'">Open (Approved)</button>
      </li>
      <li class="nav-item">
        <button class="nav-link" :class="{ active: activeTab === 'closed' }" @click="activeTab = 'closed'">Closed</button>
      </li>
      <li class="nav-item">
        <button class="nav-link" :class="{ active: activeTab === 'rejected' }" @click="activeTab = 'rejected'">Rejected</button>
      </li>
    </ul>

    <!-- Tabs Content -->
    <div v-if="isLoading" class="mt-3">
      <div class="card border-0 shadow-sm mb-3 w-100 p-4" v-for="i in 3" :key="i">
        <div class="d-flex justify-content-between align-items-center">
          <div>
            <div class="skeleton-box skeleton-title mb-2" style="width: 200px;"></div>
            <div class="skeleton-box skeleton-text" style="width: 150px;"></div>
          </div>
          <div class="d-flex gap-2">
            <div class="skeleton-box skeleton-button"></div>
            <div class="skeleton-box skeleton-button"></div>
          </div>
        </div>
      </div>
    </div>
    
    <div v-else class="tab-content">
      
      <!-- PENDING -->
      <div v-if="activeTab === 'pending'">
        <div v-if="data.pending_drives.length === 0" class="text-muted text-center py-5 bg-white rounded shadow-sm">
          No pending job drives.
        </div>
        <div v-else>
          <div v-for="drive in data.pending_drives" :key="drive.id" class="card border-0 shadow-sm mb-3 hover-card">
            <div class="card-body p-4 d-flex justify-content-between align-items-center">
              <div>
                <h5 class="fw-semibold mb-1">{{ drive.title }}</h5>
              </div>
              <div class="d-flex gap-2">
                <a v-if="drive.jd_filename" :href="`http://localhost:5000/api/files/jd/${drive.jd_filename}?token=${authState.token}`" target="_blank" class="btn btn-outline-secondary">View JD</a>
                <router-link :to="`/company/drives/${drive.id}/edit`" class="btn btn-outline-dark">Edit</router-link>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- OPEN (APPROVED) -->
      <div v-if="activeTab === 'open'">
        <div v-if="data.open_drives.length === 0" class="text-muted text-center py-5 bg-white rounded shadow-sm">
          No open job drives.
        </div>
        <div v-else>
          <div v-for="drive in data.open_drives" :key="drive.id" class="card border-0 shadow-sm mb-3 hover-card border-start border-4 border-success">
            <div class="card-body p-4 d-flex justify-content-between align-items-center">
              <div>
                <h5 class="fw-semibold mb-1">{{ drive.title }}</h5>
                <small class="text-muted"><i class="bi bi-calendar-event me-1"></i> Open till: <span class="fw-medium text-dark">{{ drive.deadline }}</span></small>
              </div>
              <div class="d-flex align-items-center gap-2">
                <a v-if="drive.jd_filename" :href="`http://localhost:5000/api/files/jd/${drive.jd_filename}?token=${authState.token}`" target="_blank" class="btn btn-outline-secondary">View JD</a>
                <router-link :to="`/company/drives/${drive.id}/edit`" class="btn btn-outline-dark">Edit Timeline</router-link>
                <router-link :to="`/company/drives/${drive.id}`" class="btn btn-dark px-4">View</router-link>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- CLOSED -->
      <div v-if="activeTab === 'closed'">
        <div v-if="data.closed_drives.length === 0" class="text-muted text-center py-5 bg-white rounded shadow-sm">
          No closed job drives.
        </div>
        <div v-else>
          <div v-for="drive in data.closed_drives" :key="drive.id" class="card border-0 shadow-sm mb-3 hover-card border-start border-4 border-secondary">
            <div class="card-body p-4 d-flex justify-content-between align-items-center">
              <div>
                <h5 class="fw-semibold mb-1 text-muted">{{ drive.title }}</h5>
              </div>
              <div class="d-flex gap-2">
                <a v-if="drive.jd_filename" :href="`http://localhost:5000/api/files/jd/${drive.jd_filename}?token=${authState.token}`" target="_blank" class="btn btn-outline-secondary">View JD</a>
                <router-link :to="`/company/drives/${drive.id}`" class="btn btn-dark px-4">Manage Applicants</router-link>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- REJECTED -->
      <div v-if="activeTab === 'rejected'">
        <div v-if="data.rejected_drives.length === 0" class="text-muted text-center py-5 bg-white rounded shadow-sm">
          No rejected job drives.
        </div>
        <div v-else>
          <div v-for="drive in data.rejected_drives" :key="drive.id" class="card border-0 shadow-sm mb-3 hover-card border-start border-4 border-danger">
            <div class="card-body p-4 d-flex justify-content-between align-items-center">
              <div>
                <h5 class="fw-semibold mb-1">{{ drive.title }}</h5>
              </div>
              <div class="d-flex gap-2">
                <a v-if="drive.jd_filename" :href="`http://localhost:5000/api/files/jd/${drive.jd_filename}?token=${authState.token}`" target="_blank" class="btn btn-outline-secondary">View JD</a>
                <router-link :to="`/company/drives/${drive.id}/edit`" class="btn btn-outline-dark">Edit & Re-submit</router-link>
              </div>
            </div>
          </div>
        </div>
      </div>

    </div>

  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { useApi } from '../../composables/useApi'
import { authState } from '../../store/auth'
import Chart from 'chart.js/auto'

const { apiFetch } = useApi()

const isLoading = ref(true)
const error = ref('')
const activeTab = ref('open')

const data = ref({
  pending_drives: [],
  open_drives: [],
  closed_drives: [],
  rejected_drives: [],
  total_applicants: 0,
  chart_drives: [],
  chart_statuses: {}
})

const fetchDrives = async () => {
  try {
    isLoading.value = true
    error.value = ''
    const response = await apiFetch('/company/drives')
    data.value = response
    
    // Auto-select tab if open is empty but others aren't
    if (response.open_drives.length === 0) {
      if (response.pending_drives.length > 0) activeTab.value = 'pending'
      else if (response.closed_drives.length > 0) activeTab.value = 'closed'
    }

    // Set isLoading false FIRST so the v-else block (containing canvases) is rendered
    isLoading.value = false

    await nextTick()
    renderCharts()
  } catch (err) {
    error.value = err.message || 'Failed to fetch drives'
    isLoading.value = false
  }
}

let driveChartInstance = null
let statusChartInstance = null

const renderCharts = () => {
  // 1. Applications per Drive (Bar Chart)
  if (data.value.chart_drives && data.value.chart_drives.length > 0) {
    const ctxDrive = document.getElementById('driveBarChart')
    if (ctxDrive) {
      if (driveChartInstance) driveChartInstance.destroy()
      
      const labels = data.value.chart_drives.map(d => d.drive_title)
      const values = data.value.chart_drives.map(d => d.count)
      
      driveChartInstance = new Chart(ctxDrive, {
        type: 'bar',
        data: {
          labels: labels,
          datasets: [{
            label: 'Applications',
            data: values,
            backgroundColor: '#0d6efd',
            borderRadius: 4,
            maxBarThickness: 40
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          indexAxis: 'y',
          plugins: { legend: { display: false } },
          scales: { x: { beginAtZero: true, ticks: { precision: 0 } } }
        }
      })
    }
  }

  // 2. Applicant Status (Pie Chart)
  if (data.value.total_applicants > 0) {
    const ctxStatus = document.getElementById('statusPieChart')
    if (ctxStatus) {
      if (statusChartInstance) statusChartInstance.destroy()
      
      const labels = Object.keys(data.value.chart_statuses)
      const values = Object.values(data.value.chart_statuses)
      
      const colorMap = {
        'Selected': '#198754',      // Success green
        'Rejected': '#dc3545',      // Danger red
        'In Progress': '#ffc107',   // Warning yellow
        'Pending': '#6c757d'        // Secondary gray
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
            legend: { position: 'bottom' }
          },
          cutout: '70%'
        }
      })
    }
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
