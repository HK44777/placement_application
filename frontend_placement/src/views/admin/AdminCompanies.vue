<template>
  <div class="container mt-4 mb-5">
    
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h4 class="fw-bold mb-1 text-dark">Manage Companies</h4>
        <p class="text-muted mb-0">Approve, reject, or suspend company accounts.</p>
      </div>
      
      <!-- Search -->
      <form @submit.prevent="fetchCompanies" class="d-flex">
        <input type="text" class="form-control me-2" placeholder="Search by name or HR..." v-model="searchQuery">
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
        <button class="nav-link" :class="{ active: activeTab === 'approved' }" @click="activeTab = 'approved'">Approved Companies</button>
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
        <div v-if="data.pending_companies.length === 0" class="text-muted text-center py-5 bg-white rounded shadow-sm">
          No companies pending approval.
        </div>
        <div v-else class="row g-3">
          <div v-for="company in data.pending_companies" :key="company.id" class="col-md-6">
            <div class="card border-0 shadow-sm h-100 hover-card">
              <div class="card-body p-4">
                <div class="d-flex justify-content-between align-items-start mb-3">
                  <div>
                    <h5 class="fw-bold mb-1">{{ company.company_name }}</h5>
                    <div class="small text-muted">{{ company.company_type || 'Type: N/A' }}</div>
                  </div>
                </div>
                <div class="small mb-1"><span class="fw-medium text-muted">Email:</span> {{ company.email }}</div>
                <div class="small mb-1"><span class="fw-medium text-muted">HR Contact:</span> {{ company.hr_contact }}</div>
                <div class="small mb-3"><span class="fw-medium text-muted">Website:</span> 
                  <a v-if="company.website" :href="company.website" target="_blank">{{ company.website }}</a>
                  <span v-else>N/A</span>
                </div>
                <div class="d-flex gap-2">
                  <button @click="handleAction('approve', company.id)" class="btn btn-success btn-sm flex-fill" :disabled="isActioning">Approve</button>
                  <button @click="handleAction('reject', company.id)" class="btn btn-danger btn-sm flex-fill" :disabled="isActioning">Reject</button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- APPROVED TAB -->
      <div v-if="activeTab === 'approved'">
        <div v-if="data.approved_companies.length === 0" class="text-muted text-center py-5 bg-white rounded shadow-sm">
          No approved companies found.
        </div>
        <div v-else class="row g-3">
          <div v-for="company in data.approved_companies" :key="company.id" class="col-md-6">
            <div class="card border-0 shadow-sm h-100 hover-card" :class="{'opacity-75': !company.is_active}">
              <div class="card-body p-4">
                <div class="d-flex justify-content-between align-items-start mb-3">
                  <div>
                    <h5 class="fw-bold mb-1">{{ company.company_name }}</h5>
                    <div class="small text-muted">{{ company.company_type || 'Type: N/A' }}</div>
                  </div>
                  <div>
                    <span v-if="company.is_active" class="badge bg-dark">Active</span>
                    <span v-else class="badge bg-secondary">Deactivated</span>
                  </div>
                </div>
                <div class="small mb-1"><span class="fw-medium text-muted">Email:</span> {{ company.email }}</div>
                <div class="small mb-1"><span class="fw-medium text-muted">HR Contact:</span> {{ company.hr_contact }}</div>
                <div class="small mb-3"><span class="fw-medium text-muted">Website:</span> 
                  <a v-if="company.website" :href="company.website" target="_blank">{{ company.website }}</a>
                  <span v-else>N/A</span>
                </div>
                
                <div class="d-flex gap-2">
                  <button v-if="!company.is_active" @click="handleAction('activate', company.id)" class="btn btn-outline-success btn-sm flex-fill" :disabled="isActioning">Activate Account</button>
                  <button v-if="company.is_active" @click="handleAction('deactivate', company.id)" class="btn btn-outline-danger btn-sm flex-fill" :disabled="isActioning">Deactivate Account</button>
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
import { ref, onMounted } from 'vue'
import { useApi } from '../../composables/useApi'
import { useModal } from '../../composables/useModal'

const { apiFetch } = useApi()
const { confirm } = useModal()

const isLoading = ref(true)
const isActioning = ref(false)
const error = ref('')
const actionSuccess = ref('')
const activeTab = ref('pending')
const searchQuery = ref('')

const data = ref({
  pending_companies: [],
  approved_companies: []
})

const fetchCompanies = async () => {
  try {
    isLoading.value = true
    error.value = ''
    
    let url = '/admin/companies'
    if (searchQuery.value) {
      url += `?search=${encodeURIComponent(searchQuery.value)}`
    }

    const response = await apiFetch(url)
    data.value = response
    
    if (response.pending_companies.length === 0 && response.approved_companies.length > 0 && !searchQuery.value) {
      activeTab.value = 'approved'
    }
  } catch (err) {
    error.value = err.message || 'Failed to fetch companies'
  } finally {
    isLoading.value = false
  }
}

const handleAction = async (action, companyId) => {
  if (action === 'deactivate') {
    const isConfirmed = await confirm('Are you sure you want to deactivate this company? This will also immediately close all of their open drives.')
    if (!isConfirmed) return
  }
  
  if (action === 'reject') {
    const isConfirmed = await confirm('Are you sure you want to reject this company profile?')
    if (!isConfirmed) return
  }

  isActioning.value = true
  error.value = ''
  actionSuccess.value = ''
  try {
    const res = await apiFetch(`/admin/companies/${companyId}/${action}`, { method: 'PUT' })
    actionSuccess.value = res.message || `Company ${action}d successfully.`
    await fetchCompanies()
  } catch (err) {
    error.value = err.message || `Failed to ${action} company`
  } finally {
    isActioning.value = false
    setTimeout(() => { actionSuccess.value = ''; error.value = '' }, 3000)
  }
}

onMounted(() => {
  fetchCompanies()
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
