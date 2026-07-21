<template>
  <div class="container mt-4 mb-5">
    
    <div v-if="error" class="alert alert-danger text-center">
      {{ error }}
    </div>

    <!-- Quick Stats Skeletons -->
    <div v-if="isLoading" class="row g-4 mb-5">
      <div class="col-md-3 col-sm-6" v-for="i in 4" :key="i">
        <div class="card border-0 shadow-sm h-100 p-3">
          <div class="skeleton-box skeleton-title mx-auto mb-2" style="width: 50%;"></div>
          <div class="skeleton-box skeleton-text mx-auto mt-2" style="width: 30%; height: 28px;"></div>
        </div>
      </div>
    </div>

    <!-- Quick Stats -->
    <div v-else class="row g-4 mb-5">
      <div class="col-md-3 col-sm-6">
        <div class="card text-center border-0 shadow-sm h-100">
          <div class="card-body">
            <div class="text-muted small fw-bold text-uppercase mb-2">Total Students</div>
            <h2 class="fw-bold mb-0 text-dark">{{ data.totals.students }}</h2>
          </div>
        </div>
      </div>
      <div class="col-md-3 col-sm-6">
        <div class="card text-center border-0 shadow-sm h-100">
          <div class="card-body">
            <div class="text-muted small fw-bold text-uppercase mb-2">Total Companies</div>
            <h2 class="fw-bold mb-0 text-dark">{{ data.totals.companies }}</h2>
          </div>
        </div>
      </div>
      <div class="col-md-3 col-sm-6">
        <div class="card text-center border-0 shadow-sm h-100">
          <div class="card-body">
            <div class="text-muted small fw-bold text-uppercase mb-2">Total Drives</div>
            <h2 class="fw-bold mb-0 text-dark">{{ data.totals.drives }}</h2>
          </div>
        </div>
      </div>
      <div class="col-md-3 col-sm-6">
        <div class="card text-center border-0 shadow-sm h-100">
          <div class="card-body">
            <div class="text-muted small fw-bold text-uppercase mb-2">Total Applications</div>
            <h2 class="fw-bold mb-0 text-dark">{{ data.totals.applications }}</h2>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Charts Skeletons -->
    <div v-if="isLoading" class="row g-4 mb-5">
      <div class="col-md-6" v-for="i in 2" :key="i">
        <div class="card border-0 shadow-sm h-100 p-4 text-center">
          <div class="skeleton-box skeleton-title mx-auto mb-4"></div>
          <div class="skeleton-box w-100 rounded-circle mx-auto" style="max-width: 200px; height: 200px;"></div>
        </div>
      </div>
    </div>

    <!-- Main Charts -->
    <div v-else class="row g-4 mb-5">
      
      <!-- Chart 1: Application Status Overview -->
      <div class="col-md-6">
        <div class="card h-100 border-0 shadow-sm">
          <div class="card-body text-center p-4">
            <h6 class="fw-semibold mb-3">Application Status Overview</h6>
            <div class="chart-container" style="position: relative; height: 300px; width: 100%;">
              <canvas v-if="Object.keys(data.charts.application_status).length > 0" id="applicationStatusChart"></canvas>
              <div v-else class="text-muted mt-5 pt-4">No data available</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Chart 2: Applications per Drive -->
      <div class="col-md-6">
        <div class="card h-100 border-0 shadow-sm">
          <div class="card-body text-center p-4">
            <h6 class="fw-semibold mb-3">Applications per Drive</h6>
            <div class="chart-container" style="position: relative; height: 300px; width: 100%;">
              <canvas v-if="Object.keys(data.charts.applications_per_drive).length > 0" id="applicationsPerDriveChart"></canvas>
              <div v-else class="text-muted mt-5 pt-4">No data available</div>
            </div>
          </div>
        </div>
      </div>

    </div>

    <!-- Secondary Charts -->
    <div v-if="!isLoading" class="row g-4 mb-5">
      
      <!-- Chart 3: Company Selections -->
      <div class="col-md-6">
        <div class="card h-100 border-0 shadow-sm">
          <div class="card-body text-center p-4">
            <h6 class="fw-semibold mb-3">Company-wise Selections</h6>
            <div class="chart-container" style="position: relative; height: 300px; width: 100%;">
              <canvas v-if="Object.keys(data.charts.company_selections).length > 0" id="companySelectionChart"></canvas>
              <div v-else class="text-muted mt-5 pt-4">No data available</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Chart 4: Branch Applications -->
      <div class="col-md-6">
        <div class="card h-100 border-0 shadow-sm">
          <div class="card-body text-center p-4">
            <h6 class="fw-semibold mb-3">Branch-wise Applications</h6>
            <div class="chart-container" style="position: relative; height: 300px; width: 100%;">
              <canvas v-if="Object.keys(data.charts.branch_applications).length > 0" id="branchApplicationsChart"></canvas>
              <div v-else class="text-muted mt-5 pt-4">No data available</div>
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
import Chart from 'chart.js/auto'

const { apiFetch } = useApi()

const isLoading = ref(true)
const error = ref('')
const data = ref({
  totals: { students: 0, companies: 0, drives: 0, applications: 0 },
  charts: {
    application_status: {},
    applications_per_drive: {},
    company_selections: {},
    branch_applications: {}
  }
})

let chartInstances = []

const fetchDashboard = async () => {
  try {
    const response = await apiFetch('/admin/dashboard')
    data.value = response
    
    // Set isLoading false FIRST so the v-else block (containing canvases) is rendered
    isLoading.value = false
    
    await nextTick()
    renderCharts()
  } catch (err) {
    error.value = err.message || 'Failed to fetch dashboard data'
    isLoading.value = false
  }
}

const renderCharts = () => {
  // Clear old instances
  chartInstances.forEach(c => c.destroy())
  chartInstances = []

  const colors = ['#4e73df', '#1cc88a', '#36b9cc', '#f6c23e', '#e74a3b', '#858796', '#5a5c69', '#2e59d9', '#17a673']
  
  const commonOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: { legend: { position: "bottom" } }
  }

  // 1. Application Status (Doughnut)
  if (Object.keys(data.value.charts.application_status).length > 0) {
    const ctx1 = document.getElementById("applicationStatusChart")
    if (ctx1) {
      const keys = Object.keys(data.value.charts.application_status)
      const values = Object.values(data.value.charts.application_status)
      chartInstances.push(new Chart(ctx1, {
        type: "doughnut",
        data: {
          labels: keys,
          datasets: [{ data: values, backgroundColor: colors, borderWidth: 1 }]
        },
        options: commonOptions
      }))
    }
  }

  // 2. Applications per Drive (Bar)
  if (Object.keys(data.value.charts.applications_per_drive).length > 0) {
    const ctx2 = document.getElementById("applicationsPerDriveChart")
    if (ctx2) {
      const keys = Object.keys(data.value.charts.applications_per_drive)
      const values = Object.values(data.value.charts.applications_per_drive)
      chartInstances.push(new Chart(ctx2, {
        type: "bar",
        data: {
          labels: keys,
          datasets: [{ label: "Applications", data: values, backgroundColor: '#4e73df', maxBarThickness: 50 }]
        },
        options: { ...commonOptions, plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true } } }
      }))
    }
  }

  // 3. Company Selections (Horizontal Bar)
  if (Object.keys(data.value.charts.company_selections).length > 0) {
    const ctx3 = document.getElementById("companySelectionChart")
    if (ctx3) {
      const keys = Object.keys(data.value.charts.company_selections)
      const values = Object.values(data.value.charts.company_selections)
      chartInstances.push(new Chart(ctx3, {
        type: "bar",
        data: {
          labels: keys,
          datasets: [{ label: "Selected", data: values, backgroundColor: '#1cc88a', maxBarThickness: 50 }]
        },
        options: { indexAxis: 'y', responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } }
      }))
    }
  }

  // 4. Branch Applications (Pie)
  if (Object.keys(data.value.charts.branch_applications).length > 0) {
    const ctx4 = document.getElementById("branchApplicationsChart")
    if (ctx4) {
      const keys = Object.keys(data.value.charts.branch_applications)
      const values = Object.values(data.value.charts.branch_applications)
      chartInstances.push(new Chart(ctx4, {
        type: "pie",
        data: {
          labels: keys,
          datasets: [{ data: values, backgroundColor: colors }]
        },
        options: commonOptions
      }))
    }
  }
}

onMounted(() => {
  fetchDashboard()
})
</script>
