<template>
  <div id="app">
    <!-- Navigation Bar - Hidden on login/register pages -->
    <nav v-if="shouldShowNavbar" class="navbar navbar-expand-lg navbar-dark bg-primary shadow-sm">
      <div class="container">
        <router-link class="navbar-brand fw-bold" to="/">
          <i class="bi bi-car-front"></i> Vehicle Parking
        </router-link>
        
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
          <span class="navbar-toggler-icon"></span>
        </button>
        
        <div class="collapse navbar-collapse" id="navbarNav">
          <ul class="navbar-nav ms-auto">
            <!-- Landing page: Show Login/Register -->
            <template v-if="$route.path === '/'">
              <li class="nav-item">
                <router-link class="nav-link" to="/login">
                  <i class="bi bi-box-arrow-in-right"></i> Login
                </router-link>
              </li>
              <li class="nav-item">
                <router-link class="nav-link" to="/register">
                  <i class="bi bi-person-plus"></i> Register
                </router-link>
              </li>
            </template>
            
            <!-- Search & Summary for authenticated users -->
            <template v-if="isLoggedIn">
              <li class="nav-item">
                <router-link class="nav-link" to="/search">
                  <i class="bi bi-search"></i> Search
                </router-link>
              </li>
              <li class="nav-item">
                <router-link class="nav-link" to="/summary">
                  <i class="bi bi-graph-up"></i> Summary
                </router-link>
              </li>
            </template>
            
            <!-- Dashboard/Profile pages: Show user dropdown only when on respective pages -->
            <li class="nav-item dropdown" v-if="($route.path === '/dashboard' && isLoggedIn && !isAdmin()) || ($route.path === '/admin' && isLoggedIn && isAdmin()) || ($route.path === '/profile' && isLoggedIn) || ($route.path === '/search' && isLoggedIn) || ($route.path === '/summary' && isLoggedIn)">
              <a class="nav-link dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown">
                <i class="bi bi-person-circle"></i> {{ currentUser?.username || 'User' }}
                <span class="badge bg-light text-primary ms-1">{{ currentUser?.role || userRole }}</span>
              </a>
              <ul class="dropdown-menu">
                <li>
                  <router-link class="dropdown-item" to="/profile">
                    <i class="bi bi-person"></i> Profile
                  </router-link>
                </li>
                <li><hr class="dropdown-divider"></li>
                <li>
                  <a class="dropdown-item" href="#" @click="logout">
                    <i class="bi bi-box-arrow-right"></i> Logout
                  </a>
                </li>
              </ul>
            </li>
          </ul>
        </div>
      </div>
    </nav>

    <!-- Main Content -->
    <main class="main-content">
      <router-view></router-view>
    </main>

    <!-- Loading Overlay -->
    <div v-if="isLoading" class="loading-overlay">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>

    <!-- Toast Notifications -->
    <div class="toast-container position-fixed top-0 end-0 p-3">
      <div v-for="toast in toasts" :key="toast.id" 
           :class="['toast', 'show', `border-${toast.type}`]" 
           role="alert">
        <div class="toast-header">
          <i :class="['bi', getToastIcon(toast.type), 'me-2']"></i>
          <strong class="me-auto">{{ getToastTitle(toast.type) }}</strong>
          <button type="button" class="btn-close" @click="removeToast(toast.id)"></button>
        </div>
        <div class="toast-body">
          {{ toast.message }}
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { authService } from './services/auth'

export default {
  name: 'App',
  setup() {
    const router = useRouter()
    const route = useRoute()
    const isLoading = ref(false)
    const toasts = ref([])
    let toastIdCounter = 0

    // Authentication state - make reactive to localStorage changes
    const userDataTrigger = ref(0) // Trigger to force reactivity
    const currentUser = computed(() => {
      userDataTrigger.value // Access trigger to make reactive
      return authService.getCurrentUser()
    })
    const isLoggedIn = computed(() => {
      userDataTrigger.value // Access trigger to make reactive
      return authService.isAuthenticated()
    })
    const userRole = computed(() => currentUser.value?.role || 'user')
    
    // Helper function to check if user is admin
    const isAdmin = () => {
      userDataTrigger.value // Access trigger to make reactive
      return authService.isAdmin()
    }
    
    // Force reactivity update
    const updateUserData = () => {
      userDataTrigger.value++
    }
    
    // Control navbar visibility based on current route
    const shouldShowNavbar = computed(() => {
      const hiddenRoutes = ['/login', '/register']
      return !hiddenRoutes.includes(route.path)
    })

    // Toast notifications
    const showToast = (message, type = 'info') => {
      const id = ++toastIdCounter
      toasts.value.push({ id, message, type })
      
      // Different durations based on toast type
      const duration = type === 'error' ? 8000 : type === 'warning' ? 7000 : 6000
      setTimeout(() => removeToast(id), duration)
    }

    const removeToast = (id) => {
      const index = toasts.value.findIndex(toast => toast.id === id)
      if (index > -1) {
        toasts.value.splice(index, 1)
      }
    }

    const getToastIcon = (type) => {
      const icons = {
        success: 'bi-check-circle',
        error: 'bi-exclamation-circle',
        warning: 'bi-exclamation-triangle',
        info: 'bi-info-circle'
      }
      return icons[type] || icons.info
    }

    const getToastTitle = (type) => {
      const titles = {
        success: 'Success',
        error: 'Error',
        warning: 'Warning',
        info: 'Information'
      }
      return titles[type] || titles.info
    }

    // Logout function
    const logout = async () => {
      try {
        console.log('Starting logout process...')
        isLoggingOut = true // Prevent router.afterEach from interfering
        
        // First clear the authentication data
        await authService.logout()
        console.log('Auth service logout completed')
        
        // Force immediate reactive update to clear user state
        updateUserData()
        console.log('User data updated')
        
        // Navigate to landing page immediately without delay
        console.log('Navigating to landing page...')
        await router.replace('/') // Use replace instead of push to avoid history issues
        
        // Re-enable router.afterEach
        isLoggingOut = false
        
        // Show success message
        showToast('Logged out successfully', 'success')
        console.log('Logout process completed')
      } catch (error) {
        console.error('Logout error:', error)
        isLoggingOut = false
        showToast('Logout failed', 'error')
        
        // Force clear everything and navigate
        localStorage.clear()
        updateUserData()
        router.replace('/')
      }
    }

    // Refresh user data
    const refreshUserData = async () => {
      if (authService.isAuthenticated()) {
        try {
          await authService.getProfile()
          updateUserData() // Force reactive update
        } catch (error) {
          console.error('Failed to refresh user data:', error)
        }
      }
    }

    // Watch for route changes and refresh user data (disabled during logout)
    let isLoggingOut = false
    router.afterEach(() => {
      if (!isLoggingOut) {
        refreshUserData()
      }
    })

    // Provide global functions
    window.showToast = showToast
    window.setLoading = (loading) => { isLoading.value = loading }

    onMounted(() => {
      // App initialization - refresh user data to ensure current session
      refreshUserData()
      
      // Listen for storage changes to update user data reactively
      const handleStorageChange = (e) => {
        if (e.key === 'user' || e.key === 'access_token') {
          updateUserData()
        }
      }
      
      window.addEventListener('storage', handleStorageChange)
      
      // Custom event listener for same-window storage changes
      const originalSetItem = localStorage.setItem
      localStorage.setItem = function(key, value) {
        originalSetItem.apply(this, arguments)
        if (key === 'user' || key === 'access_token') {
          updateUserData()
        }
      }
    })

    return {
      isLoading,
      toasts,
      currentUser,
      isLoggedIn,
      userRole,
      isAdmin,
      shouldShowNavbar,
      logout,
      removeToast,
      getToastIcon,
      getToastTitle
    }
  }
}
</script>

<style>
/* Global Styles */
#app {
  min-height: 100vh;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.main-content {
  min-height: calc(100vh - 56px);
  padding-top: 0;
}

/* Loading Overlay */
.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999;
}

/* Custom Cards */
.custom-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 15px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

/* Buttons */
.btn-gradient {
  background: linear-gradient(45deg, #667eea, #764ba2);
  border: none;
  color: white;
  transition: all 0.3s ease;
}

.btn-gradient:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
  color: white;
}

/* Animations */
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s;
}
.fade-enter, .fade-leave-to {
  opacity: 0;
}

/* Toast Styling */
.toast {
  backdrop-filter: blur(10px);
  background: rgba(255, 255, 255, 0.95);
}

/* Responsive Design */
@media (max-width: 768px) {
  .main-content {
    padding: 1rem;
  }
}
</style>