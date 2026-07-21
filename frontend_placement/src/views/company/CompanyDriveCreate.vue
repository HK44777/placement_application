<template>
  <div class="container mt-4 mb-5 d-flex justify-content-center">
    <div class="card shadow-sm border-0 w-100" style="max-width: 800px;">
      <div class="card-body p-5">
        <h4 class="card-title fw-bold mb-1 text-dark">Create Job Drive</h4>
        <p class="text-muted mb-3 small">Post a new placement opportunity for students.</p>
        <div class="text-muted small mb-4"><span class="text-danger fw-bold">*</span> Indicates a mandatory field</div>

        <div class="mb-4">
          <router-link to="/company/dashboard" class="back-btn">Back to Dashboard</router-link>
        </div>
        
        <form @submit.prevent="handleSubmit" novalidate>
          <div class="row g-3 mb-3">
            <div class="col-md-8">
              <label class="form-label fw-medium text-dark">Job Title <span class="text-danger">*</span></label>
              <input type="text" class="form-control" :class="{'is-invalid': fieldErrors.title}" v-model="form.title" placeholder="e.g. Software Engineer">
              <div v-if="fieldErrors.title" class="invalid-feedback">{{ fieldErrors.title[0] }}</div>
            </div>
            <div class="col-md-4">
              <label class="form-label fw-medium text-dark">CTC (in LPA) <span class="text-danger">*</span></label>
              <input type="number" step="0.1" class="form-control" :class="{'is-invalid': fieldErrors.ctc}" v-model="form.ctc" placeholder="e.g. 12.5">
              <div v-if="fieldErrors.ctc" class="invalid-feedback">{{ fieldErrors.ctc[0] }}</div>
            </div>
          </div>

          <div class="row g-3 mb-3">
            <div class="col-md-6">
              <label class="form-label fw-medium text-dark">Application Deadline <span class="text-danger">*</span></label>
              <input type="date" class="form-control" :class="{'is-invalid': fieldErrors.deadline}" v-model="form.deadline">
              <div v-if="fieldErrors.deadline" class="invalid-feedback">{{ fieldErrors.deadline[0] }}</div>
            </div>
            <div class="col-md-6">
              <label class="form-label fw-medium text-dark">Minimum CGPA Required <span class="text-danger">*</span></label>
              <input type="number" step="0.1" class="form-control" :class="{'is-invalid': fieldErrors.min_cgpa}" v-model="form.min_cgpa" placeholder="0.0 to 10.0">
              <div v-if="fieldErrors.min_cgpa" class="invalid-feedback">{{ fieldErrors.min_cgpa[0] }}</div>
            </div>
          </div>

          <div class="row g-3 mb-3">
            <div class="col-md-6">
              <label class="form-label fw-medium text-dark">History of Backlogs Allowed? <span class="text-danger">*</span></label>
              <select class="form-select" :class="{'is-invalid': fieldErrors.history_backlog_allowed}" v-model="form.history_backlog_allowed" @change="form.history_backlog_allowed === 'No' ? form.allowed_active_backlogs = 0 : null">
                <option value="No">No</option>
                <option value="Yes">Yes</option>
              </select>
              <div v-if="fieldErrors.history_backlog_allowed" class="invalid-feedback">{{ fieldErrors.history_backlog_allowed[0] }}</div>
            </div>
            <div class="col-md-6">
              <label class="form-label fw-medium text-dark">Allowed Active Backlogs <span class="text-danger">*</span></label>
              <input type="number" class="form-control" :class="{'is-invalid': fieldErrors.allowed_active_backlogs}" v-model="form.allowed_active_backlogs" placeholder="0" :disabled="form.history_backlog_allowed === 'No'">
              <div v-if="fieldErrors.allowed_active_backlogs" class="invalid-feedback">{{ fieldErrors.allowed_active_backlogs[0] }}</div>
            </div>
          </div>

          <div class="mb-3">
            <label class="form-label fw-medium text-dark">Allowed Branches <span class="text-danger">*</span></label>
            <!-- Selected Tags -->
            <div class="mb-2 d-flex flex-wrap gap-2">
              <span v-for="branch in form.allowed_branches" :key="branch" class="badge bg-dark d-flex align-items-center py-2 px-3">
                {{ branch }}
                <button type="button" class="btn-close btn-close-white ms-2" style="font-size: 0.65rem;" @click="removeBranch(branch)" aria-label="Remove"></button>
              </span>
            </div>
            <!-- Dropdown -->
            <select class="form-select" :class="{'is-invalid': fieldErrors.allowed_branches}" @change="addBranch($event.target.value); $event.target.value = ''">
              <option value="" disabled selected>Select a branch to add...</option>
              <option v-for="b in availableBranches" :key="b.value" :value="b.value">{{ b.label }}</option>
            </select>
            <div v-if="fieldErrors.allowed_branches" class="invalid-feedback d-block">{{ fieldErrors.allowed_branches[0] }}</div>
          </div>

          <div class="mb-3">
            <label class="form-label fw-medium text-dark">Allowed Graduation Years <span class="text-danger">*</span></label>
            <!-- Selected Tags -->
            <div class="mb-2 d-flex flex-wrap gap-2">
              <span v-for="year in form.allowed_grad_years" :key="year" class="badge bg-dark d-flex align-items-center py-2 px-3">
                {{ year }}
                <button type="button" class="btn-close btn-close-white ms-2" style="font-size: 0.65rem;" @click="removeYear(year)" aria-label="Remove"></button>
              </span>
            </div>
            <!-- Dropdown -->
            <select class="form-select" :class="{'is-invalid': fieldErrors.allowed_grad_years}" @change="addYear($event.target.value); $event.target.value = ''">
              <option value="" disabled selected>Select a year to add...</option>
              <option v-for="y in availableYears" :key="y" :value="y">{{ y }}</option>
            </select>
            <div v-if="fieldErrors.allowed_grad_years" class="invalid-feedback d-block">{{ fieldErrors.allowed_grad_years[0] }}</div>
          </div>

          <div class="mb-4">
            <label class="form-label fw-medium text-dark">Required Skills <span class="text-muted fw-normal">(Optional)</span></label>
            <input type="text" class="form-control" :class="{'is-invalid': fieldErrors.skills_required}" v-model="form.skills_required" placeholder="e.g. Python, Vue, AWS">
            <div v-if="fieldErrors.skills_required" class="invalid-feedback">{{ fieldErrors.skills_required[0] }}</div>
          </div>

          <hr class="text-muted opacity-25 mb-4">
          <h5 class="fw-bold mb-3 text-dark">Interview Rounds <span class="text-danger">*</span></h5>
          <div class="alert alert-secondary small py-2 mb-3">
            Define up to 5 interview rounds. Give each round a name and a scheduled date.
          </div>
          <div v-if="fieldErrors.rounds" class="alert alert-danger small py-2 mb-3">
            {{ fieldErrors.rounds[0] }}
          </div>

          <div v-for="i in 5" :key="i" class="row g-2 mb-2 align-items-center">
            <div class="col-md-1 text-center text-muted fw-bold">{{ i }}.</div>
            <div class="col-md-6">
              <input type="text" class="form-control form-control-sm" :placeholder="`Round ${i} Name (e.g. Aptitude)`" v-model="form[`round_name_${i}`]">
            </div>
            <div class="col-md-5">
              <input type="date" class="form-control form-control-sm" v-model="form[`round_date_${i}`]">
            </div>
          </div>

          <hr class="text-muted opacity-25 my-4">
          <h5 class="fw-bold mb-3 text-dark">Job Description (JD)</h5>
          
          <div class="mb-4">
            <label class="form-label fw-medium text-dark">Upload JD PDF Document <span class="text-danger">*</span></label>
            <FileUpload v-model="jdFile" accept=".pdf" :error="!!fieldErrors.jd" />
            <div v-if="fieldErrors.jd" class="d-block invalid-feedback">{{ fieldErrors.jd[0] }}</div>
            <div class="form-text mt-2">Must be a PDF file under 5MB.</div>
          </div>

          <div class="d-flex justify-content-end gap-2 mt-5">
            <router-link to="/company/dashboard" class="btn btn-light border px-4">Cancel</router-link>
            <button type="submit" class="btn btn-dark px-4 fw-medium" :disabled="isSubmitting">
              {{ isSubmitting ? 'Submitting...' : 'Submit for Approval' }}
            </button>
          </div>
        </form>

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useApi } from '../../composables/useApi'
import { toast } from 'vue3-toastify'
import FileUpload from '../../components/FileUpload.vue'

const router = useRouter()
const { apiFetch } = useApi()

const isSubmitting = ref(false)
const fieldErrors = ref({})
const jdFile = ref(null)

const ALL_BRANCHES = [
  { value: 'CSE', label: 'Computer Science and Engg (CSE)' },
  { value: 'ISE', label: 'Information Science and Engg (ISE)' },
  { value: 'ECE', label: 'Electronics and Communication Engg (ECE)' },
  { value: 'MECH', label: 'Mechanical Engg (MECH)' },
  { value: 'CIVIL', label: 'Civil Engg (CIVIL)' },
  { value: 'EEE', label: 'Electrical and Electronics Engg (EEE)' }
]
const ALL_YEARS = ['2024', '2025', '2026', '2027', '2028']

const availableBranches = computed(() => ALL_BRANCHES.filter(b => !form.value.allowed_branches.includes(b.value)))
const availableYears = computed(() => ALL_YEARS.filter(y => !form.value.allowed_grad_years.includes(y)))

const addBranch = (val) => {
  if (val && !form.value.allowed_branches.includes(val)) {
    form.value.allowed_branches.push(val)
  }
}
const removeBranch = (val) => {
  form.value.allowed_branches = form.value.allowed_branches.filter(b => b !== val)
}

const addYear = (val) => {
  if (val && !form.value.allowed_grad_years.includes(val)) {
    form.value.allowed_grad_years.push(val)
  }
}
const removeYear = (val) => {
  form.value.allowed_grad_years = form.value.allowed_grad_years.filter(y => y !== val)
}

const form = ref({
  title: '',
  ctc: '',
  deadline: '',
  min_cgpa: '',
  history_backlog_allowed: 'No',
  allowed_active_backlogs: 0,
  allowed_branches: [],
  allowed_grad_years: [],
  skills_required: '',
  round_name_1: '', round_date_1: '',
  round_name_2: '', round_date_2: '',
  round_name_3: '', round_date_3: '',
  round_name_4: '', round_date_4: '',
  round_name_5: '', round_date_5: ''
})

const handleSubmit = async () => {
  fieldErrors.value = {}
  let isValid = true

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

  if (!form.value.deadline) {
    fieldErrors.value.deadline = ['An application deadline must be scheduled.']
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
  
  if (form.value.history_backlog_allowed === 'No' && form.value.allowed_active_backlogs > 0) {
    fieldErrors.value.allowed_active_backlogs = ['Active backlogs must be 0 if history of backlogs is not allowed.']
    isValid = false
  }

  if (form.value.allowed_branches.length === 0) {
    fieldErrors.value.allowed_branches = ['Please select at least one allowed branch.']
    isValid = false
  }

  if (form.value.allowed_grad_years.length === 0) {
    fieldErrors.value.allowed_grad_years = ['Please select at least one allowed graduation year.']
    isValid = false
  }

  if (!jdFile.value) {
    fieldErrors.value.jd = ['Please upload the official Job Description document in PDF format.']
    isValid = false
  }

  // Check if at least one round is provided
  let hasRound = false
  for (let i = 1; i <= 5; i++) {
    if (form.value[`round_name_${i}`] && form.value[`round_name_${i}`].trim() !== '') {
      hasRound = true
      break
    }
  }
  if (!hasRound) {
    fieldErrors.value.rounds = ['At least one interview round is required.']
    isValid = false
  }

  if (!isValid) {
    toast.error('Please correct the highlighted fields.')
    return
  }

  isSubmitting.value = true

  const formData = new FormData()
  // Append all standard fields
  Object.keys(form.value).forEach(key => {
    const val = form.value[key]
    if (val !== '' && (!Array.isArray(val) || val.length > 0)) {
      if (Array.isArray(val)) {
        formData.append(key, val.join(','))
      } else {
        formData.append(key, val)
      }
    }
  })
  
  try {
    // 1. Get presigned URL for S3 upload
    if (jdFile.value) {
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

    // 4. Send the rest of the form to backend
    await apiFetch('/company/drives', {
      method: 'POST',
      body: formData
    })
    
    toast.success('Drive created successfully! Awaiting approval. Redirecting...')
    setTimeout(() => {
      router.push('/company/dashboard')
    }, 2500)
  } catch (error) {
    if (error.validationErrors) {
      fieldErrors.value = error.validationErrors
      toast.error('Please fix the highlighted errors.')
    } else {
      toast.error(error.message || 'Failed to create drive')
    }
  } finally {
    isSubmitting.value = false
  }
}
</script>
