<template>
  <!-- Confirm Modal -->
  <div class="modal fade" id="globalConfirmModal" tabindex="-1" aria-hidden="true">
    <div class="modal-dialog modal-dialog-centered">
      <div class="modal-content border-0 shadow">
        <div class="modal-header bg-dark text-white border-bottom-0 pb-3">
          <h5 class="modal-title fw-bold">{{ modalState.confirmTitle }}</h5>
          <button type="button" class="btn-close btn-close-white" @click="handleConfirm(false)" aria-label="Close"></button>
        </div>
        <div class="modal-body py-4">
          <p class="mb-0 fs-5">{{ modalState.confirmMessage }}</p>
        </div>
        <div class="modal-footer border-top-0 pt-0">
          <button type="button" class="btn btn-secondary px-4" @click="handleConfirm(false)">Cancel</button>
          <button type="button" class="btn btn-danger px-4" @click="handleConfirm(true)">Confirm</button>
        </div>
      </div>
    </div>
  </div>

  <!-- Alert Modal -->
  <div class="modal fade" id="globalAlertModal" tabindex="-1" aria-hidden="true">
    <div class="modal-dialog modal-dialog-centered">
      <div class="modal-content border-0 shadow">
        <div class="modal-header bg-dark text-white border-bottom-0 pb-3">
          <h5 class="modal-title fw-bold">{{ modalState.alertTitle }}</h5>
          <button type="button" class="btn-close btn-close-white" @click="handleAlertClose" aria-label="Close"></button>
        </div>
        <div class="modal-body py-4">
          <p class="mb-0 fs-5">{{ modalState.alertMessage }}</p>
        </div>
        <div class="modal-footer border-top-0 pt-0">
          <button type="button" class="btn btn-dark px-4" @click="handleAlertClose">OK</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, watch } from 'vue'
import { modalState } from '../composables/useModal'

let confirmModalInstance = null
let alertModalInstance = null

onMounted(() => {
  confirmModalInstance = new window.bootstrap.Modal(document.getElementById('globalConfirmModal'), {
    backdrop: 'static',
    keyboard: false
  })
  
  alertModalInstance = new window.bootstrap.Modal(document.getElementById('globalAlertModal'), {
    backdrop: 'static',
    keyboard: false
  })
})

// Watchers wait a tick using basic reactivity to hide/show 
// based on composable state
watch(() => modalState.showConfirm, (newVal) => {
  if (newVal && confirmModalInstance) {
    confirmModalInstance.show()
  } else if (!newVal && confirmModalInstance) {
    confirmModalInstance.hide()
  }
})

watch(() => modalState.showAlert, (newVal) => {
  if (newVal && alertModalInstance) {
    alertModalInstance.show()
  } else if (!newVal && alertModalInstance) {
    alertModalInstance.hide()
  }
})

const handleConfirm = (result) => {
  if (modalState.resolveConfirm) {
    modalState.resolveConfirm(result)
    modalState.resolveConfirm = null
  }
  modalState.showConfirm = false
}

const handleAlertClose = () => {
  if (modalState.resolveAlert) {
    modalState.resolveAlert()
    modalState.resolveAlert = null
  }
  modalState.showAlert = false
}
</script>
