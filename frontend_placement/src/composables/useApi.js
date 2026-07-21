import { authState, setAuth, clearAuth } from '../store/auth'
import router from '../router'

const BASE_URL = 'http://localhost:5000/api'

export function useApi() {
  /**
   * Wrapper around fetch to automatically handle Authorization headers
   * and intercept 401s for token refreshing.
   */
  const apiFetch = async (endpoint, options = {}) => {
    let url = `${BASE_URL}${endpoint}`
    
    // Set up default headers
    const headers = new Headers(options.headers || {})
    if (!(options.body instanceof FormData)) {
      if (!headers.has('Content-Type')) {
        headers.set('Content-Type', 'application/json')
      }
    }
    
    if (authState.token) {
      headers.set('Authorization', `Bearer ${authState.token}`)
    }
    
    const fetchOptions = {
      ...options,
      headers,
      credentials: 'include' // Important for sending/receiving HTTPOnly cookies
    }

    try {
      let response = await fetch(url, fetchOptions)

      // Handle 401 Unauthorized (Token expired or missing)
      if (response.status === 401 && !endpoint.includes('/auth/login')) {
        // Try refreshing token
        const refreshed = await refreshToken()
        if (refreshed) {
          // Retry original request with new token
          fetchOptions.headers.set('Authorization', `Bearer ${authState.token}`)
          response = await fetch(url, fetchOptions)
        } else {
          // Refresh failed, logout
          clearAuth()
          router.push('/login')
          throw new Error('Session expired. Please login again.')
        }
      }
      
      const data = await response.json().catch(() => null)

      if (!response.ok) {
        let errMsg = data?.message || 'An error occurred'
        let validationErrors = null
        
        // 1. Check if 'detail' is a string
        if (typeof data?.detail === 'string') {
          errMsg = data.detail
        } 
        // 2. Check if 'detail' is an object containing our custom 'error' string
        else if (data?.detail && typeof data.detail === 'object' && !Array.isArray(data.detail)) {
          if (data.detail.error) {
            errMsg = data.detail.error
          }
          // Check for custom validation details array inside the detail object
          if (Array.isArray(data.detail.details)) {
            validationErrors = {}
            data.detail.details.forEach(err => {
              const field = err.loc[err.loc.length - 1]
              if (!validationErrors[field]) {
                validationErrors[field] = []
              }
              validationErrors[field].push(err.msg)
            })
          }
        } 
        // 3. Fallback for root-level 'error' string
        else if (typeof data?.error === 'string') {
          errMsg = data.error
        }
        
        // 4. Check for standard FastAPI validation errors (detail is an array)
        const detailsArray = data?.details || (Array.isArray(data?.detail) ? data.detail : null)
        if (detailsArray && Array.isArray(detailsArray)) {
          validationErrors = {}
          detailsArray.forEach(err => {
            const field = err.loc[err.loc.length - 1]
            if (!validationErrors[field]) {
              validationErrors[field] = []
            }
            validationErrors[field].push(err.msg)
          })
          if (errMsg === 'An error occurred') errMsg = 'Validation failed'
        } else if (data?.error && typeof data.error === 'object' && data.error !== null) {
          validationErrors = data.error
          if (errMsg === 'An error occurred') errMsg = 'Validation failed'
        }
        
        const error = new Error(errMsg)
        error.validationErrors = validationErrors
        throw error
      }

      return data
    } catch (error) {
      throw error
    }
  }

  const refreshToken = async () => {
    try {
      const response = await fetch(`${BASE_URL}/auth/refresh`, {
        method: 'POST',
        credentials: 'include'
      })
      const data = await response.json()
      
      if (response.ok && data.access_token) {
        setAuth(data.access_token, authState.role, authState.user_id)
        return true
      }
      return false
    } catch (error) {
      return false
    }
  }

  return { apiFetch }
}
