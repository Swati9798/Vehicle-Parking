<template>
  <div class="home-container">
    <div class="container py-5">
      <!-- Hero Section -->
      <div class="row align-items-center min-vh-100">
        <div class="col-lg-6">
          <div class="hero-content">
            <h1 class="display-4 fw-bold text-white mb-4">
              Smart Parking Made Simple
            </h1>
            <p class="lead text-white-50 mb-4">
              Find, book, and manage parking spots effortlessly. Our intelligent parking system 
              helps you secure your spot in advance and tracks your parking history.
            </p>
            <div class="d-grid gap-2 d-md-flex">
              <router-link to="/register" class="btn btn-light btn-lg px-4 me-md-2">
                <i class="bi bi-person-plus"></i> Get Started
              </router-link>
              <router-link to="/login" class="btn btn-outline-light btn-lg px-4">
                <i class="bi bi-box-arrow-in-right"></i> Sign In
              </router-link>
            </div>
          </div>
        </div>
        <div class="col-lg-6">
          <div class="hero-image text-center">
            <div class="parking-graphic">
              <i class="bi bi-car-front-fill display-1 text-white"></i>
              <div class="parking-spots mt-4">
                <div class="row g-2">
                  <div class="col-4" v-for="n in 6" :key="n">
                    <div class="parking-spot" :class="{ 'occupied': n <= 3 }">
                      <i class="bi bi-car-front" v-if="n <= 3"></i>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Features Section -->
      <div class="row py-5">
        <div class="col-12 text-center mb-5">
          <h2 class="display-5 fw-bold text-white">Why Choose Our Parking System?</h2>
          <p class="lead text-white-50">Experience the future of parking management</p>
        </div>
        
        <div class="col-md-4 mb-4">
          <div class="feature-card custom-card h-100 p-4 text-center">
            <div class="feature-icon mb-3">
              <i class="bi bi-geo-alt-fill text-primary display-4"></i>
            </div>
            <h4 class="fw-bold mb-3">Real-time Availability</h4>
            <p class="text-muted">
              Check available parking spots in real-time across multiple locations. 
              Never waste time searching for parking again.
            </p>
          </div>
        </div>
        
        <div class="col-md-4 mb-4">
          <div class="feature-card custom-card h-100 p-4 text-center">
            <div class="feature-icon mb-3">
              <i class="bi bi-clock-fill text-success display-4"></i>
            </div>
            <h4 class="fw-bold mb-3">Quick Booking</h4>
            <p class="text-muted">
              Book your parking spot in seconds with our streamlined booking process. 
              Reserve now, park later.
            </p>
          </div>
        </div>
        
        <div class="col-md-4 mb-4">
          <div class="feature-card custom-card h-100 p-4 text-center">
            <div class="feature-icon mb-3">
              <i class="bi bi-shield-check-fill text-warning display-4"></i>
            </div>
            <h4 class="fw-bold mb-3">Secure & Reliable</h4>
            <p class="text-muted">
              Your reservations are secure and guaranteed. Track your parking history 
              and manage payments seamlessly.
            </p>
          </div>
        </div>
      </div>

      <!-- Stats Section (if user is logged in) -->
      <div v-if="isLoggedIn && stats" class="row py-5">
        <div class="col-12 text-center mb-4">
          <h3 class="fw-bold text-white">System Overview</h3>
        </div>
        <div class="col-md-3 mb-3">
          <div class="stat-card custom-card p-4 text-center">
            <i class="bi bi-building text-primary display-5"></i>
            <h3 class="fw-bold mt-2">{{ stats.total_lots || 0 }}</h3>
            <p class="text-muted mb-0">Parking Lots</p>
          </div>
        </div>
        <div class="col-md-3 mb-3">
          <div class="stat-card custom-card p-4 text-center">
            <i class="bi bi-square text-info display-5"></i>
            <h3 class="fw-bold mt-2">{{ stats.total_spots || 0 }}</h3>
            <p class="text-muted mb-0">Total Spots</p>
          </div>
        </div>
        <div class="col-md-3 mb-3">
          <div class="stat-card custom-card p-4 text-center">
            <i class="bi bi-check-circle text-success display-5"></i>
            <h3 class="fw-bold mt-2">{{ stats.available_spots || 0 }}</h3>
            <p class="text-muted mb-0">Available</p>
          </div>
        </div>
        <div class="col-md-3 mb-3">
          <div class="stat-card custom-card p-4 text-center">
            <i class="bi bi-person-fill text-warning display-5"></i>
            <h3 class="fw-bold mt-2">{{ stats.total_users || 0 }}</h3>
            <p class="text-muted mb-0">Users</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { authService } from '../services/auth'
import { adminService } from '../services/parking'

export default {
  name: 'Home',
  setup() {
    const stats = ref(null)

    const isLoggedIn = computed(() => authService.isAuthenticated())
    const currentUser = computed(() => authService.getCurrentUser())
    const userRole = computed(() => currentUser.value?.role || 'user')

    const loadStats = async () => {
      if (isLoggedIn.value && userRole.value === 'admin') {
        const result = await adminService.getDashboardData()
        if (result.success) {
          stats.value = result.data
        }
      }
    }

    onMounted(() => {
      loadStats()
    })

    return {
      stats,
      isLoggedIn,
      currentUser,
      userRole
    }
  }
}
</script>

<style scoped>
.home-container {
  min-height: 100vh;
}

.hero-content {
  animation: fadeInUp 1s ease-out;
}

.hero-image {
  animation: fadeInRight 1s ease-out 0.3s both;
}

.parking-graphic {
  position: relative;
}

.parking-spots {
  max-width: 300px;
  margin: 0 auto;
}

.parking-spot {
  height: 60px;
  background: rgba(255, 255, 255, 0.2);
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.parking-spot.occupied {
  background: rgba(255, 193, 7, 0.8);
  border-color: #ffc107;
}

.parking-spot i {
  font-size: 1.5rem;
  color: #333;
}

.feature-card {
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.feature-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
}

.stat-card {
  transition: transform 0.3s ease;
}

.stat-card:hover {
  transform: scale(1.05);
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes fadeInRight {
  from {
    opacity: 0;
    transform: translateX(30px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

@media (max-width: 768px) {
  .hero-content {
    text-align: center;
    margin-bottom: 3rem;
  }
  
  .parking-spots {
    max-width: 250px;
  }
  
  .parking-spot {
    height: 40px;
  }
}
</style>