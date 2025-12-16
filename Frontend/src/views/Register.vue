<template>
  <div class="register-container">
    <div class="container">
      <div class="row justify-content-center align-items-center min-vh-100">
        <div class="col-md-8 col-lg-6">
          <div class="register-card custom-card p-5">
            <div class="text-center mb-4">
              <i class="bi bi-person-plus-fill text-primary display-4"></i>
              <h2 class="fw-bold mt-3">Join Us Today</h2>
              <p class="text-muted">Create your parking account</p>
            </div>

            <!-- Flash Error Message -->
            <div v-if="persistentError" class="alert alert-danger d-flex align-items-center mb-4" role="alert">
              <i class="bi bi-exclamation-triangle-fill me-2"></i>
              <div>{{ persistentError }}</div>
              <button type="button" class="btn-close ms-auto" @click="clearPersistentError"></button>
            </div>

            <form @submit.prevent="handleRegister">
              <div class="row">
                <div class="col-md-6 mb-3">
                  <label class="form-label fw-bold">Username</label>
                  <div class="input-group">
                    <span class="input-group-text">
                      <i class="bi bi-person"></i>
                    </span>
                    <input 
                      type="text" 
                      class="form-control"
                      v-model="registerForm.username"
                      placeholder="Choose a username"
                    >
                  </div>
                </div>

                <div class="col-md-6 mb-3">
                  <label class="form-label fw-bold">Email</label>
                  <div class="input-group">
                    <span class="input-group-text">
                      <i class="bi bi-envelope"></i>
                    </span>
                    <input 
                      type="email" 
                      class="form-control"
                      v-model="registerForm.email"
                      placeholder="Enter your email"
                    >
                  </div>
                </div>
              </div>

              <div class="row">
                <div class="col-md-6 mb-3">
                  <label class="form-label fw-bold">Password</label>
                  <div class="input-group">
                    <span class="input-group-text">
                      <i class="bi bi-lock"></i>
                    </span>
                    <input 
                      :type="showPassword ? 'text' : 'password'"
                      class="form-control"
                      v-model="registerForm.password"
                      placeholder="Create a password"
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

                <div class="col-md-6 mb-3">
                  <label class="form-label fw-bold">Confirm Password</label>
                  <div class="input-group">
                    <span class="input-group-text">
                      <i class="bi bi-lock-fill"></i>
                    </span>
                    <input 
                      :type="showConfirmPassword ? 'text' : 'password'"
                      class="form-control"
                      v-model="confirmPassword"
                      placeholder="Confirm your password"
                    >
                    <button 
                      type="button" 
                      class="btn btn-outline-secondary"
                      @click="showConfirmPassword = !showConfirmPassword"
                    >
                      <i :class="showConfirmPassword ? 'bi bi-eye-slash' : 'bi bi-eye'"></i>
                    </button>
                  </div>
                </div>
              </div>
              <div class="d-grid mb-3">
                <button 
                  type="submit" 
                  class="btn btn-gradient btn-lg"
                  :disabled="isLoading || !isFormValid"
                >
                  <span v-if="isLoading" class="spinner-border spinner-border-sm me-2"></span>
                  <i v-else class="bi bi-person-plus me-2"></i>
                  {{ isLoading ? 'Creating Account...' : 'Create Account' }}
                </button>
              </div>

              <div class="text-center">
                <p class="mb-0">
                  Already have an account? 
                  <router-link to="/login" class="text-decoration-none fw-bold">
                    Sign in here
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
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { authService } from '../services/auth'

export default {
  name: 'Register',
  setup() {
    const router = useRouter()
    const isLoading = ref(false)
    const showPassword = ref(false)
    const showConfirmPassword = ref(false)
    const acceptTerms = ref(false)
    const persistentError = ref('')
    
    const registerForm = ref({
      username: '',
      email: '',
      password: ''
    })
    
    const confirmPassword = ref('')

    // Check for stored errors on mount
    onMounted(() => {
      checkStoredError()
    })

    const checkStoredError = () => {
      const storedError = localStorage.getItem('register_error')
      if (storedError) {
        try {
          const errorData = JSON.parse(storedError)
          const errorAge = Date.now() - errorData.timestamp
          
          // Show error if it's less than 5 minutes old
          if (errorAge < 300000) {
            persistentError.value = errorData.message
          }
          // Always remove the stored error after checking
          localStorage.removeItem('register_error')
        } catch (e) {
          localStorage.removeItem('register_error')
        }
      }
    }

    const storeError = (message) => {
      localStorage.setItem('register_error', JSON.stringify({
        message: message,
        timestamp: Date.now()
      }))
      persistentError.value = message
    }

    const clearPersistentError = () => {
      persistentError.value = ''
      localStorage.removeItem('register_error')
    }
    const passwordStrength = computed(() => {
      const password = registerForm.value.password
      if (!password) return { width: '0%', class: '', text: '' }
      
      let score = 0
      if (password.length >= 6) score++
      if (password.length >= 8) score++
      if (/[A-Z]/.test(password)) score++
      if (/[0-9]/.test(password)) score++
      if (/[^A-Za-z0-9]/.test(password)) score++
      
      if (score <= 2) return { width: '25%', class: 'weak', text: 'Weak password' }
      if (score <= 3) return { width: '50%', class: 'fair', text: 'Fair password' }
      if (score <= 4) return { width: '75%', class: 'good', text: 'Good password' }
      return { width: '100%', class: 'strong', text: 'Strong password' }
    })

    // Form validation - Button always highlighted
    const isFormValid = computed(() => {
      return true  // Button always highlighted regardless of form state
    })

    const handleRegister = async () => {
      // Clear any existing error
      clearPersistentError()
      
      // Check if any field is empty first (general check)
      if (!registerForm.value.username.trim() || 
          !registerForm.value.email.trim() || 
          !registerForm.value.password || 
          !confirmPassword.value) {
        storeError('Please fill in all required fields')
        return
      }
      
      // Then do specific validations
      if (!registerForm.value.username.trim()) {
        storeError('Please enter a username')
        return
      }
      
      if (!registerForm.value.email.trim()) {
        storeError('Please enter an email address')
        return
      }
      
      if (!registerForm.value.email.includes('@') || !registerForm.value.email.includes('.')) {
        storeError('Please enter a valid email address')
        return
      }
      
      if (!registerForm.value.password) {
        storeError('Please enter a password')
        return
      }
      
      if (registerForm.value.password.length < 6) {
        storeError('Password must be at least 6 characters long')
        return
      }
      
      if (!confirmPassword.value) {
        storeError('Please confirm your password')
        return
      }
      
      if (registerForm.value.password !== confirmPassword.value) {
        storeError('Passwords do not match')
        return
      }

      isLoading.value = true
      
      try {
        const result = await authService.register(registerForm.value)
        
        if (result.success) {
          clearPersistentError()
          router.push('/login')
        } else {
          storeError(result.message || 'Registration failed. Please try again.')
        }
      } catch (error) {
        storeError('Registration failed. Please try again.')
      } finally {
        isLoading.value = false
      }
    }

    const goToLandingPage = () => {
      router.push('/')
    }

    return {
      registerForm,
      confirmPassword,
      isLoading,
      showPassword,
      showConfirmPassword,
      acceptTerms,
      passwordStrength,
      persistentError,
      isFormValid,
      handleRegister,
      clearPersistentError,
      goToLandingPage
    }
  }
}
</script>

<style scoped>
.register-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.register-card {
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

.password-strength {
  margin-top: 0.5rem;
}

.strength-bar {
  height: 4px;
  background: #e9ecef;
  border-radius: 2px;
  overflow: hidden;
}

.strength-fill {
  height: 100%;
  transition: all 0.3s ease;
}

.strength-fill.weak {
  background: #dc3545;
}

.strength-fill.fair {
  background: #fd7e14;
}

.strength-fill.good {
  background: #ffc107;
}

.strength-fill.strong {
  background: #198754;
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
  .register-card {
    margin: 1rem;
    padding: 2rem !important;
  }
}
</style>