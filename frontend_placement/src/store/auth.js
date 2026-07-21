import { reactive } from 'vue'

export const authState = reactive({
  token: localStorage.getItem('access_token') || null,
  user_id: localStorage.getItem('user_id') || null,
  role: localStorage.getItem('role') || null,
  isAuthenticated: !!localStorage.getItem('access_token')
})

export const setAuth = (token, role, userId) => {
  authState.token = token
  authState.role = role
  authState.user_id = userId
  authState.isAuthenticated = true
  
  localStorage.setItem('access_token', token)
  if (role) localStorage.setItem('role', role)
  if (userId) localStorage.setItem('user_id', userId)
}

export const clearAuth = () => {
  authState.token = null
  authState.role = null
  authState.user_id = null
  authState.isAuthenticated = false
  
  localStorage.removeItem('access_token')
  localStorage.removeItem('role')
  localStorage.removeItem('user_id')
}
