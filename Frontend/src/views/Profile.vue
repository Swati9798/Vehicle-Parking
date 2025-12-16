<template>
  <div class="profile-container">
    <div class="container">
      <div class="row justify-content-center">
        <div class="col-md-8 col-lg-6">
          <div class="profile-card">
            <div class="profile-header">
              <div class="profile-avatar">
                <i class="bi bi-person-circle"></i>
              </div>
              <h2 class="profile-title">My Profile</h2>
            </div>
            
            <div class="profile-content">
              <!-- Loading State -->
              <div v-if="loading" class="text-center py-4">
                <div class="spinner-border text-primary" role="status">
                  <span class="visually-hidden">Loading...</span>
                </div>
                <p class="mt-2">Loading profile...</p>
              </div>

              <!-- Error State -->
              <div v-else-if="error" class="alert alert-danger" role="alert">
                <i class="bi bi-exclamation-triangle-fill"></i>
                {{ error }}
              </div>

              <!-- Profile Information -->
              <div v-else class="profile-info">
                
                <div class="info-group">
                  <label class="info-label">
                    <i class="bi bi-at"></i>
                    Username
                  </label>
                  <div class="info-value">{{ userInfo.username || 'Not provided' }}</div>
                </div>
                
                <div class="info-group">
                  <label class="info-label">
                    <i class="bi bi-envelope-fill"></i>
                    Email Address
                  </label>
                  <div class="info-value">{{ userInfo.email || 'Not provided' }}</div>
                </div>
                
                <div class="info-group">
                  <label class="info-label">
                    <i class="bi bi-shield-fill-check"></i>
                    Role
                  </label>
                  <div class="info-value">
                    <span class="role-badge" :class="userInfo.role?.toLowerCase()">
                      {{ userInfo.role || 'User' }}
                    </span>
                  </div>
                </div>
              </div>
              
              <div class="profile-actions" v-if="!loading && !error">
                <button class="btn btn-outline-secondary" @click="backToDashboard">
                  <i class="bi bi-arrow-left"></i>
                  Back to Dashboard
                </button>
              </div>
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
import apiClient from '../services/api'

export default {
  name: 'Profile',
  setup() {
    const router = useRouter()
    const userInfo = ref({})
    const loading = ref(true)
    const error = ref('')

    const loadUserProfile = async () => {
      try {
        loading.value = true
        error.value = ''
        
        // Check if user is authenticated
        if (!authService.isAuthenticated()) {
          router.push('/login')
          return
        }

        // Fetch user profile from backend
        const response = await apiClient.get('/auth/profile')
        if (response.data && response.data.data) {
          userInfo.value = response.data.data
          console.log('User profile loaded:', userInfo.value)
        } else {
          throw new Error('Invalid response format')
        }
      } catch (error) {
        console.error('Failed to load user profile:', error)
        error.value = 'Failed to load profile information'
        
        // If token is invalid, redirect to login
        if (error.response?.status === 401) {
          authService.logout()
          router.push('/login')
        }
      } finally {
        loading.value = false
      }
    }

    const formatDate = (dateString) => {
      if (!dateString) return 'Not available'
      try {
        return new Date(dateString).toLocaleDateString('en-US', {
          year: 'numeric',
          month: 'long',
          day: 'numeric'
        })
      } catch (error) {
        return 'Not available'
      }
    }

    const backToDashboard = () => {
      // Navigate to appropriate dashboard based on user role
      if (authService.isAdmin()) {
        router.push('/admin')
      } else {
        router.push('/dashboard')
      }
    }

    onMounted(() => {
      loadUserProfile()
    })

    return {
      userInfo,
      loading,
      error,
      formatDate,
      backToDashboard
    }
  }
}
</script>

<style scoped>
.profile-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 2rem 0;
}

.profile-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  padding: 0;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.3);
  overflow: hidden;
}

.profile-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 2rem;
  text-align: center;
  position: relative;
}

.profile-avatar {
  margin-bottom: 1rem;
}

.profile-avatar i {
  font-size: 4rem;
  opacity: 0.9;
}

.profile-title {
  margin: 0;
  font-weight: 600;
  font-size: 1.8rem;
}

.profile-content {
  padding: 2rem;
}

.profile-info {
  margin-bottom: 2rem;
}

.info-group {
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
}

.info-group:last-child {
  border-bottom: none;
  margin-bottom: 0;
}

.info-label {
  display: flex;
  align-items: center;
  font-weight: 600;
  color: #555;
  margin-bottom: 0.5rem;
  font-size: 0.9rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.info-label i {
  margin-right: 0.5rem;
  color: #667eea;
}

.info-value {
  font-size: 1.1rem;
  color: #333;
  padding-left: 1.5rem;
}

.role-badge {
  display: inline-block;
  padding: 0.3rem 0.8rem;
  border-radius: 15px;
  font-size: 0.85rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.role-badge.admin {
  background: linear-gradient(135deg, #ff6b6b, #ee5a24);
  color: white;
}

.role-badge.user {
  background: linear-gradient(135deg, #4ecdc4, #44a08d);
  color: white;
}

.status-badge {
  display: inline-block;
  padding: 0.3rem 0.8rem;
  border-radius: 15px;
  font-size: 0.85rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.status-badge.active {
  background: linear-gradient(135deg, #51cf66, #40c057);
  color: white;
}

.status-badge.inactive {
  background: linear-gradient(135deg, #ff6b6b, #ff5252);
  color: white;
}

.profile-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
}

.btn {
  padding: 0.75rem 1.5rem;
  border-radius: 25px;
  font-weight: 600;
  transition: all 0.3s ease;
  border: none;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
}

.btn-outline-secondary {
  background: transparent;
  border: 2px solid #6c757d;
  color: #6c757d;
}

.btn-outline-secondary:hover {
  background: #6c757d;
  color: white;
  transform: translateY(-2px);
  box-shadow: 0 10px 20px rgba(108, 117, 125, 0.3);
}

@media (max-width: 768px) {
  .profile-container {
    padding: 1rem 0;
  }
  
  .profile-header,
  .profile-content {
    padding: 1.5rem;
  }
  
  .profile-actions {
    flex-direction: column;
  }
  
  .btn {
    width: 100%;
    justify-content: center;
  }
}
</style>