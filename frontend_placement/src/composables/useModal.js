import { reactive } from 'vue'

export const modalState = reactive({
  showConfirm: false,
  confirmMessage: '',
  confirmTitle: 'Confirm',
  resolveConfirm: null,
  
  showAlert: false,
  alertMessage: '',
  alertTitle: 'Alert',
  resolveAlert: null
})

export function useModal() {
  const confirm = (message, title = 'Confirm') => {
    return new Promise((resolve) => {
      modalState.confirmMessage = message
      modalState.confirmTitle = title
      modalState.resolveConfirm = resolve
      modalState.showConfirm = true
    })
  }

  const alert = (message, title = 'Alert') => {
    return new Promise((resolve) => {
      modalState.alertMessage = message
      modalState.alertTitle = title
      modalState.resolveAlert = resolve
      modalState.showAlert = true
    })
  }

  return { confirm, alert }
}
