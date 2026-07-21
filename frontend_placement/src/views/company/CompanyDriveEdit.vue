<template>
  <div class="container mt-4 mb-5 d-flex justify-content-center">
    <div v-if="isLoading" class="text-center mt-5 w-100">
      <div class="spinner-border text-dark" role="status"></div>
    </div>
    
    <div v-else class="card shadow-sm border-0 w-100" style="max-width: 800px;">
      <div class="card-body p-5">
        
        <h4 class="card-title fw-bold mb-1 text-dark">Edit Job Drive</h4>
        <p class="text-muted mb-4 small">
          {{ isFullEdit ? 'Update details for your pending or rejected drive.' : 'Update timeline (deadline and rounds) for your approved drive.' }}
        </p>

        <div v-if="globalError" class="alert alert-danger mb-4">
          {{ globalError }}
        </div>

        <div v-if="successMessage" class="alert alert-success mb-4 text-center">
          {{ successMessage }}
        </div>

        <form @submit.prevent="handleSubmit" novalidate>
          
          <!-- ============================ -->
          <!-- FULL EDIT (Pending/Rejected) -->
          <!-- ============================ -->
          <div v-if="isFullEdit">
            <div class="row g-3 mb-3">
              <div class="col-md-8">
                <label class="form-label fw-medium text-dark">Job Title</label>
                <input type="text" class="form-control" :class="{'is-invalid': fieldErrors.title}" v-model="form.title">
                <div v-if="fieldErrors.title" class="invalid-feedback">{{ fieldErrors.title[0] }}</div>
              </div>
              <div class="col-md-4">
                <label class="form-label fw-medium text-dark">CTC (in LPA)</label>
                <input type="number" step="0.1" class="form-control" :class="{'is-invalid': fieldErrors.ctc}" v-model="form.ctc">
                <div v-if="fieldErrors.ctc" class="invalid-feedback">{{ fieldErrors.ctc[0] }}</div>
              </div>
            </div>

            <div class="row g-3 mb-3">
              <div class="col-md-6">
                <label class="form-label fw-medium text-dark">Minimum CGPA Required</label>
                <input type="number" step="0.1" class="form-control" :class="{'is-invalid': fieldErrors.min_cgpa}" v-model="form.min_cgpa">
                <div v-if="fieldErrors.min_cgpa" class="invalid-feedback">{{ fieldErrors.min_cgpa[0] }}</div>
              </div>
              <div class="col-md-6">
                <label class="form-label fw-medium text-dark">Allowed Active Backlogs</label>
                <input type="number" class="form-control" :class="{'is-invalid': fieldErrors.allowed_active_backlogs}" v-model="form.allowed_active_backlogs">
                <div v-if="fieldErrors.allowed_active_backlogs" class="invalid-feedback">{{ fieldErrors.allowed_active_backlogs[0] }}</div>
              </div>
            </div>

            <div class="row g-3 mb-3">
              <div class="col-md-6">
                <label class="form-label fw-medium text-dark">History of Backlogs Allowed?</label>
                <select class="form-select" :class="{'is-invalid': fieldErrors.history_backlog_allowed}" v-model="form.history_backlog_allowed">
                  <option value="No">No</option>
                  <option value="Yes">Yes</option>
                </select>
                <div v-if="fieldErrors.history_backlog_allowed" class="invalid-feedback">{{ fieldErrors.history_backlog_allowed[0] }}</div>
              </div>
              <div class="col-md-6">
                <label class="form-label fw-medium text-dark">Allowed Branches</label>
                <input type="text" class="form-control" :class="{'is-invalid': fieldErrors.allowed_branches}" v-model="form.allowed_branches">
                <div v-if="fieldErrors.allowed_branches" class="invalid-feedback">{{ fieldErrors.allowed_branches[0] }}</div>
              </div>
            </div>

            <div class="mb-3">
              <label class="form-label fw-medium text-dark">Allowed Graduation Years</label>
              <input type="text" class="form-control" :class="{'is-invalid': fieldErrors.allowed_grad_years}" v-model="form.allowed_grad_years">
              <div v-if="fieldErrors.allowed_grad_years" class="invalid-feedback">{{ fieldErrors.allowed_grad_years[0] }}</div>
            </div>

            <div class="mb-4">
              <label class="form-label fw-medium text-dark">Required Skills</label>
              <input type="text" class="form-control" :class="{'is-invalid': fieldErrors.skills_required}" v-model="form.skills_required">
              <div v-if="fieldErrors.skills_required" class="invalid-feedback">{{ fieldErrors.skills_required[0] }}</div>
            </div>
            
            <hr class="text-muted opacity-25 my-4">
          </div>

          <!-- ============================ -->
          <!-- SHARED FIELDS (Timeline) -->
          <!-- ============================ -->
          
          <div class="mb-4">
            <label class="form-label fw-medium text-dark">Application Deadline</label>
            <input type="date" class="form-control" :class="{'is-invalid': fieldErrors.deadline}" v-model="form.deadline">
            <div v-if="fieldErrors.deadline" class="invalid-feedback">{{ fieldErrors.deadline[0] }}</div>
          </div>

          <h5 class="fw-bold mb-3 text-dark">Interview Rounds</h5>
          <div v-if="fieldErrors.rounds" class="alert alert-danger small py-2 mb-3">
            {{ fieldErrors.rounds[0] }}
          </div>
          <div v-for="i in 5" :key="i" class="row g-2 mb-2 align-items-center">
            <div class="col-md-1 text-center text-muted fw-bold">{{ i }}.</div>
            <div class="col-md-6">
              <input type="text" class="form-control form-control-sm" :placeholder="`Round ${i} Name`" v-model="form[`round_name_${i}`]">
            </div>
            <div class="col-md-5">
              <input type="date" class="form-control form-control-sm" v-model="form[`round_date_${i}`]">
            </div>
          </div>

          <!-- ============================ -->
          <!-- JD UPLOAD (Full Edit Only) -->
          <!-- ============================ -->
          <div v-if="isFullEdit">
            <hr class="text-muted opacity-25 my-4">
            <h5 class="fw-bold mb-3 text-dark">Job Description (JD)</h5>
            <div class="mb-4">
              <label class="form-label fw-medium text-dark">Upload New JD PDF (Optional)</label>
              <FileUpload v-model="jdFile" accept=".pdf" :error="!!fieldErrors.jd" />
              <div v-if="fieldErrors.jd" class="d-block invalid-feedback">{{ fieldErrors.jd[0] }}</div>
              <div class="form-text mt-2">Leave empty to keep the existing JD document.</div>
            </div>
          </div>

          <!-- Submit Buttons -->
          <div class="d-flex justify-content-end gap-2 mt-5">
            <router-link to="/company/dashboard" class="btn btn-light border px-4">Cancel</router-link>
            <button type="submit" class="btn btn-dark px-4 fw-medium" :disabled="isSubmitting">
              {{ isSubmitting ? 'Saving...' : 'Save Changes' }}
            </button>
          </div>

        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useApi } from '../../composables/useApi'
import FileUpload from '../../components/FileUpload.vue'

const router = useRouter()
const route = useRoute()
const { apiFetch } = useApi()

const driveId = route.params.id

const isLoading = ref(true)
const isSubmitting = ref(false)
const globalError = ref('')
const successMessage = ref('')
const fieldErrors = ref({})
const jdFile = ref(null)

const isFullEdit = ref(false) // true for Pending/Rejected, false for Approved

const form = ref({
  title: '', ctc: '', deadline: '', min_cgpa: '', history_backlog_allowed: '',
  allowed_active_backlogs: '', allowed_branches: '', allowed_grad_years: '', skills_required: '',
  round_name_1: '', round_date_1: '',
  round_name_2: '', round_date_2: '',
  round_name_3: '', round_date_3: '',
  round_name_4: '', round_date_4: '',
  round_name_5: '', round_date_5: ''
})

const fetchDrive = async () => {
  try {
    const data = await apiFetch(`/company/drives/${driveId}`)
    
    // Determine Edit Mode
    if (data.approval_status === 'Pending' || data.approval_status === 'Rejected') {
      isFullEdit.value = true
    } else if (data.approval_status === 'Approved') {
      isFullEdit.value = false
    } else {
      globalError.value = "This drive cannot be edited."
    }

    // Populate common fields
    form.value.deadline = data.deadline
    
    // Populate rounds
    if (data.rounds) {
      data.rounds.forEach((r, idx) => { form.value[`round_name_${idx + 1}`] = r })
    }
    if (data.round_dates) {
      data.round_dates.forEach((d, idx) => { form.value[`round_date_${idx + 1}`] = d })
    }

    // Populate full edit fields
    if (isFullEdit.value) {
      form.value.title = data.title
      form.value.ctc = data.ctc
      form.value.min_cgpa = data.min_cgpa
      form.value.history_backlog_allowed = data.history_backlog_allowed
      form.value.allowed_active_backlogs = data.allowed_active_backlogs
      form.value.allowed_branches = data.allowed_branches.join(', ')
      form.value.allowed_grad_years = data.allowed_grad_years.join(', ')
      form.value.skills_required = data.skills_required || ''
    }

  } catch (err) {
    globalError.value = err.message || 'Failed to fetch drive details'
  } finally {
    isLoading.value = false
  }
}

const handleSubmit = async () => {
  globalError.value = ''
  successMessage.value = ''
  fieldErrors.value = {}
  let isValid = true

  if (isFullEdit.value) {
    if (!form.value.title.trim()) {
      fieldErrors.value.title = ['A professional title for the job drive is required.']
      isValid = false
    }
    if (form.value.ctc === '' || form.value.ctc === null) {
      fieldErrors.value.ctc = ['Please specify the Compensation (CTC) offered.']
      isValid = false
    } else if (isNaN(form.value.ctc) || form.value.ctc < 0) {
      fieldErrors.value.ctc = ['CTC must be a valid positive number.']
      isValid = false
    }
    if (form.value.min_cgpa === '' || form.value.min_cgpa === null) {
      fieldErrors.value.min_cgpa = ['Please define the minimum CGPA criterion.']
      isValid = false
    } else if (isNaN(form.value.min_cgpa) || form.value.min_cgpa < 0 || form.value.min_cgpa > 10) {
      fieldErrors.value.min_cgpa = ['Minimum CGPA must be between 0 and 10.']
      isValid = false
    }
    if (form.value.allowed_active_backlogs === '' || form.value.allowed_active_backlogs === null) {
      fieldErrors.value.allowed_active_backlogs = ['Please specify the maximum number of active backlogs allowed.']
      isValid = false
    } else if (isNaN(form.value.allowed_active_backlogs) || form.value.allowed_active_backlogs < 0) {
      fieldErrors.value.allowed_active_backlogs = ['Active backlogs must be 0 or greater.']
      isValid = false
    }
  }

  if (!form.value.deadline) {
    fieldErrors.value.deadline = ['An application deadline must be scheduled.']
    isValid = false
  }

  if (!isValid) {
    return
  }

  isSubmitting.value = true

  const formData = new FormData()

  // For Timeline Edit, we only send deadline + rounds
  const keysToSend = isFullEdit.value 
    ? Object.keys(form.value) 
    : ['deadline', 'round_name_1', 'round_date_1', 'round_name_2', 'round_date_2', 
       'round_name_3', 'round_date_3', 'round_name_4', 'round_date_4', 'round_name_5', 'round_date_5']

  keysToSend.forEach(key => {
    if (form.value[key] !== '' && form.value[key] !== null) {
      formData.append(key, form.value[key])
    }
  })
  
  try {
    if (isFullEdit.value && jdFile.value) {
      // 1. Get presigned URL for S3 upload
      const presignRes = await apiFetch('/files/presigned-url', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          file_name: jdFile.value.name,
          file_type: jdFile.value.type || 'application/pdf',
          folder: 'jd'
        })
      })

      if (!presignRes.url) {
        throw new Error("Failed to get presigned URL for JD upload")
      }

      // 2. Upload directly to S3
      const s3Res = await fetch(presignRes.url, {
        method: 'PUT',
        headers: {
          'Content-Type': jdFile.value.type || 'application/pdf'
        },
        body: jdFile.value
      })

      if (!s3Res.ok) {
        throw new Error("Failed to upload JD to S3")
      }

      // 3. Append the object key instead of the file
      formData.append('jd_key', presignRes.object_key)
    }

    await apiFetch(`/company/drives/${driveId}`, {
      method: 'PUT',
      body: formData 
    })
    successMessage.value = 'Drive updated successfully! Redirecting...'
    setTimeout(() => {
      router.push('/company/dashboard')
    }, 1500)
  } catch (error) {
    if (error.validationErrors) {
      fieldErrors.value = error.validationErrors
    } else {
      globalError.value = error.message || 'Failed to update drive'
    }
  } finally {
    isSubmitting.value = false
  }
}

onMounted(() => {
  fetchDrive()
})
</script>
