<template>
  <div class="login-container">
    <div class="container">
      <div class="row justify-content-center align-items-center min-vh-100">
        <div class="col-md-6 col-lg-5">
          <div class="login-card custom-card p-5">
            <div class="text-center mb-4">
              <i class="bi bi-car-front-fill text-primary display-4"></i>
              <h2 class="fw-bold mt-3">Welcome Back</h2>
              <p class="text-muted">Sign in to your parking account</p>
            </div>

            <!-- Persistent Error Display -->
            <div v-if="persistentError" class="alert alert-danger d-flex align-items-center mb-4" role="alert">
              <i class="bi bi-exclamation-triangle-fill me-2"></i>
              <div>{{ persistentError }}</div>
              <button type="button" class="btn-close ms-auto" @click="clearPersistentError"></button>
            </div>

            <form @submit.prevent="handleLogin" @submit="$event.preventDefault()">
              <div class="mb-3">
                <label class="form-label fw-bold">Username</label>
                <div class="input-group">
                  <span class="input-group-text">
                    <i class="bi bi-person"></i>
                  </span>
                  <input 
                    type="text" 
                    class="form-control"
                    v-model="loginForm.username"
                    placeholder="Enter your username"
                    required
                  >
                </div>
              </div>

              <div class="mb-4">
                <label class="form-label fw-bold">Password</label>
                <div class="input-group">
                  <span class="input-group-text">
                    <i class="bi bi-lock"></i>
                  </span>
                  <input 
                    :type="showPassword ? 'text' : 'password'"
                    class="form-control"
                    v-model="loginForm.password"
                    placeholder="Enter your password"
                    required
                  >
                  <button 
                    type="button" 
                    class="btn btn-outline-secondary"
                    @click="showPassword = !showPassword"
                  >
                    <i :class="showPassword ? 'bi bi-eye-slash' : 'bi bi-eye'"></i>
                  </button>
                </div>
              </div>

              <div class="d-grid mb-3">
                <button 
                  type="button" 
                  class="btn btn-gradient btn-lg"
                  :disabled="isLoading"
                  @click="handleLogin"
                >
                  <span v-if="isLoading" class="spinner-border spinner-border-sm me-2"></span>
                  <i v-else class="bi bi-box-arrow-in-right me-2"></i>
                  {{ isLoading ? 'Signing In...' : 'Sign In' }}
                </button>
              </div>

              <div class="text-center">
                <p class="mb-0">
                  Don't have an account? 
                  <router-link to="/register" class="text-decoration-none fw-bold">
                    Create one here
                  </router-link>
                </p>
              </div>
            </form>

            <!-- Back to Landing Page Button -->
            <div class="text-center mt-4">
              <button type="button" class="btn btn-outline-secondary" @click="goToLandingPage">
                <i class="bi bi-arrow-left me-2"></i>Back to Landing Page
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { authService } from '../services/auth'

export default {
  name: 'Login',
  setup() {
    const router = useRouter()
    const isLoading = ref(false)
    const showPassword = ref(false)
    
    const loginForm = ref({
      username: '',
      password: ''
    })

    const persistentError = ref('')

    // Clear persistent error
    const clearPersistentError = () => {
      persistentError.value = ''
      localStorage.removeItem('login_error')
    }

    // Check for persistent login errors on component mount
    const checkForStoredError = () => {
      const storedError = localStorage.getItem('login_error')
      if (storedError) {
        try {
          const errorData = JSON.parse(storedError)
          const errorAge = Date.now() - errorData.timestamp
          
          // Show error if it's less than 5 minutes old
          if (errorAge < 300000) {
            persistentError.value = errorData.message
            // Don't show toast notification - only show the alert box
          } else {
            // Remove old errors
            localStorage.removeItem('login_error')
          }
        } catch (e) {
          // Remove corrupted error data
          localStorage.removeItem('login_error')
        }
      }
    }

    // Mount lifecycle
    onMounted(() => {
      checkForStoredError()
    })

    const handleLogin = async (event) => {
      // Prevent any form submission/page refresh
      if (event) {
        event.preventDefault()
        event.stopPropagation()
      }
      
      // Clear any existing error
      localStorage.removeItem('login_error')
      persistentError.value = ''
      
      if (!loginForm.value.username || !loginForm.value.password) {
        const errorMsg = 'Please fill in all fields'
        localStorage.setItem('login_error', JSON.stringify({
          message: errorMsg,
          timestamp: Date.now()
        }))
        persistentError.value = errorMsg
        // Don't show toast - only show alert box
        return
      }

      isLoading.value = true
      
      try {
        console.log('Attempting login with:', loginForm.value)
        const result = await authService.login(loginForm.value)
        console.log('Login result:', result)
        
        if (result.success) {
          // Clear any error on successful login
          localStorage.removeItem('login_error')
          persistentError.value = ''
          // Don't show success toast - just redirect
          
          // Redirect based on user role
          if (result.user.role === 'admin') {
            router.push('/admin')
          } else {
            router.push('/dashboard')
          }
        } else {
          console.log('Login failed with message:', result.message)
          const errorMsg = result.message || 'Invalid username or password'
          
          // Store error persistently
          localStorage.setItem('login_error', JSON.stringify({
            message: errorMsg,
            timestamp: Date.now()
          }))
          persistentError.value = errorMsg
          
          // Don't show toast - only show alert box
        }
      } catch (error) {
        console.error('Login catch error:', error)
        const errorMsg = 'Login failed. Please try again.'
        
        // Store error persistently
        localStorage.setItem('login_error', JSON.stringify({
          message: errorMsg,
          timestamp: Date.now()
        }))
        persistentError.value = errorMsg
        
        // Don't show toast - only show alert box
      } finally {
        isLoading.value = false
      }
    }

    const goToLandingPage = () => {
      router.push('/')
    }

    return {
      loginForm,
      isLoading,
      showPassword,
      persistentError,
      handleLogin,
      clearPersistentError,
      goToLandingPage
    }
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-card {
  animation: slideInUp 0.6s ease-out;
}

.input-group-text {
  background: rgba(102, 126, 234, 0.1);
  border-color: rgba(102, 126, 234, 0.2);
  color: #667eea;
}

.form-control:focus {
  border-color: #667eea;
  box-shadow: 0 0 0 0.2rem rgba(102, 126, 234, 0.25);
}

@keyframes slideInUp {
  from {
    opacity: 0;
    transform: translateY(50px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (max-width: 768px) {
  .login-card {
    margin: 1rem;
    padding: 2rem !important;
  }
}
</style>