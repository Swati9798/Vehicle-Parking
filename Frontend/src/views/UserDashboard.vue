<template>
  <div class="user-dashboard">
    <div class="container-fluid py-4">
      <!-- Welcome Header -->
      <div class="row mb-4">
        <div class="col-12">
          <div class="welcome-header custom-card p-4">
            <div class="row align-items-center">
              <div class="col-md-8">
                <h1 class="fw-bold mb-2">
                  Welcome back, {{ currentUser?.username }}! 
                  <i class="bi bi-waving-hand text-warning"></i>
                </h1>
                <p class="text-muted mb-0">Manage your parking reservations and find available spots</p>
              </div>
              <div class="col-md-4 text-md-end">
                <div class="current-time">
                  <small class="text-muted">{{ currentDateTime }}</small>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Quick Stats -->
      <div class="row mb-4">
        <div class="col-md-4 mb-3">
          <div class="stat-card custom-card p-4 text-center h-100">
            <i class="bi bi-bookmark-check-fill text-success display-5"></i>
            <h3 class="fw-bold mt-2">{{ activeReservations.length }}</h3>
            <p class="text-muted mb-0">Active Reservations</p>
          </div>
        </div>
        <div class="col-md-4 mb-3">
          <div class="stat-card custom-card p-4 text-center h-100">
            <i class="bi bi-clock-history text-info display-5"></i>
            <h3 class="fw-bold mt-2">{{ totalReservations.length }}</h3>
            <p class="text-muted mb-0">Total Bookings</p>
          </div>
        </div>
        <div class="col-md-4 mb-3">
          <div class="stat-card custom-card p-4 text-center h-100">
            <i class="bi bi-building text-primary display-5"></i>
            <h3 class="fw-bold mt-2">{{ parkingLots.length }}</h3>
            <p class="text-muted mb-0">Available Lots</p>
          </div>
        </div>
      </div>

      <!-- Main Content -->
      <div class="row">
        <!-- Current Reservations -->
        <div class="col-lg-6 mb-4">
          <div class="reservations-card custom-card p-4 h-100">
            <div class="d-flex justify-content-between align-items-center mb-3">
              <h4 class="fw-bold mb-0">
                <i class="bi bi-car-front text-primary me-2"></i>
                Current Reservations
              </h4>
              <button class="btn btn-outline-primary btn-sm" @click="loadReservations">
                <i class="bi bi-arrow-clockwise"></i>
              </button>
            </div>

            <div v-if="activeReservations.length === 0" class="text-center py-4">
              <i class="bi bi-car-front text-muted display-4"></i>
              <p class="text-muted mt-2">No active reservations</p>
              <button class="btn btn-primary" @click="showBookingModal = true">
                <i class="bi bi-plus-circle me-2"></i>Book a Spot
              </button>
            </div>

            <div v-else>
              <div v-for="reservation in activeReservations" :key="reservation.id" 
                   class="reservation-item border rounded p-3 mb-3">
                <div class="row align-items-center">
                  <div class="col-md-8">
                    <div class="d-flex align-items-center mb-2">
                      <span class="badge bg-success me-2">Active</span>
                      <h6 class="mb-0">Spot #{{ reservation.spot_id }}</h6>
                    </div>
                    <p class="text-muted mb-1">
                      <i class="bi bi-geo-alt me-1"></i>
                      {{ getParkingLotName(reservation.spot_id) }}
                    </p>
                    <p class="text-muted mb-1">
                      <i class="bi bi-clock me-1"></i>
                      {{ formatDateTime(reservation.parking_timestamp) }}
                    </p>
                    <p class="text-muted mb-0">
                      <i class="bi bi-stopwatch me-1"></i>
                      Duration: {{ reservation.duration_hours?.toFixed(1) || 0 }}h
                    </p>
                  </div>
                  <div class="col-md-4 text-md-end">
                    <button 
                      class="btn btn-outline-danger btn-sm"
                      @click="releaseSpot(reservation.id)"
                      :disabled="isLoading"
                    >
                      <i class="bi bi-box-arrow-right me-1"></i>
                      Release
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Available Parking Lots -->
        <div class="col-lg-6 mb-4">
          <div class="parking-lots-card custom-card p-4 h-100">
            <div class="d-flex justify-content-between align-items-center mb-3">
              <h4 class="fw-bold mb-0">
                <i class="bi bi-building text-success me-2"></i>
                Available Parking Lots
              </h4>
              <button class="btn btn-outline-success btn-sm" @click="loadParkingLots">
                <i class="bi bi-arrow-clockwise"></i>
              </button>
            </div>

            <div v-if="parkingLots.length === 0" class="text-center py-4">
              <i class="bi bi-building text-muted display-4"></i>
              <p class="text-muted mt-2">No parking lots available</p>
            </div>

            <div v-else class="parking-lots-list" style="max-height: 400px; overflow-y: auto;">
              <div v-for="lot in parkingLots" :key="lot.id" 
                   class="lot-item border rounded p-3 mb-3 cursor-pointer"
                   @click="selectLot(lot)">
                <div class="row align-items-center">
                  <div class="col-md-8">
                    <h6 class="fw-bold mb-1">{{ lot.prime_location_name }}</h6>
                    <p class="text-muted mb-1">
                      <i class="bi bi-geo-alt me-1"></i>{{ lot.address }}
                    </p>
                    <p class="text-muted mb-0">
                      <i class="bi bi-currency-dollar me-1"></i>${{ lot.price_per_hour }}/hour
                    </p>
                  </div>
                  <div class="col-md-4 text-md-end">
                    <div class="availability-badge">
                      <span class="badge bg-primary">
                        {{ lot.available_spots_count || 0 }} / {{ lot.number_of_spots }}
                      </span>
                      <small class="d-block text-muted">Available</small>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Recent Reservations History -->
      <div class="row">
        <div class="col-12">
          <div class="history-card custom-card p-4">
            <h4 class="fw-bold mb-3">
              <i class="bi bi-clock-history text-info me-2"></i>
              Recent Reservations
            </h4>

            <div v-if="recentReservations.length === 0" class="text-center py-4">
              <i class="bi bi-clock-history text-muted display-4"></i>
              <p class="text-muted mt-2">No reservation history</p>
            </div>

            <div v-else class="table-responsive">
              <table class="table table-hover">
                <thead>
                  <tr>
                    <th>Spot</th>
                    <th>Location</th>
                    <th>Check-in</th>
                    <th>Check-out</th>
                    <th>Duration</th>
                    <th>Cost</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="reservation in recentReservations" :key="reservation.id">
                    <td>#{{ reservation.spot_id }}</td>
                    <td>{{ getParkingLotName(reservation.spot_id) }}</td>
                    <td>{{ formatDateTime(reservation.parking_timestamp) }}</td>
                    <td>{{ reservation.leaving_timestamp ? formatDateTime(reservation.leaving_timestamp) : '-' }}</td>
                    <td>{{ reservation.duration_hours?.toFixed(1) || 0 }}h</td>
                    <td>${{ reservation.parking_cost?.toFixed(2) || '0.00' }}</td>
                    <td>
                      <span :class="['badge', reservation.is_active ? 'bg-success' : 'bg-secondary']">
                        {{ reservation.is_active ? 'Active' : 'Completed' }}
                      </span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Booking Modal -->
    <div v-if="showBookingModal" class="modal-overlay" @click="showBookingModal = false">
      <div class="modal-content custom-card" @click.stop>
        <div class="modal-header border-bottom pb-3 mb-3">
          <h5 class="fw-bold mb-0">Book Parking Spot</h5>
          <button class="btn-close" @click="showBookingModal = false"></button>
        </div>
        
        <div class="modal-body">
          <div v-if="!selectedLot" class="text-center py-4">
            <p class="text-muted">Please select a parking lot from the available lots list.</p>
            <button class="btn btn-outline-primary" @click="showBookingModal = false">
              Go Back to Select
            </button>
          </div>
          
          <div v-else>
            <div class="lot-details mb-4 p-3 bg-light rounded">
              <h6 class="fw-bold">{{ selectedLot.prime_location_name }}</h6>
              <p class="text-muted mb-1">{{ selectedLot.address }}</p>
              <p class="text-muted mb-0">Rate: ${{ selectedLot.price_per_hour }}/hour</p>
            </div>

            <form @submit.prevent="bookSpot">
              <div class="mb-3">
                <label class="form-label fw-bold">Vehicle Number</label>
                <input 
                  type="text" 
                  class="form-control"
                  v-model="bookingForm.vehicle_number"
                  placeholder="Enter your vehicle number"
                  required
                >
              </div>
              
              <div class="d-grid gap-2">
                <button 
                  type="submit" 
                  class="btn btn-gradient"
                  :disabled="isLoading"
                >
                  <span v-if="isLoading" class="spinner-border spinner-border-sm me-2"></span>
                  <i v-else class="bi bi-check-circle me-2"></i>
                  {{ isLoading ? 'Booking...' : 'Confirm Booking' }}
                </button>
                <button 
                  type="button" 
                  class="btn btn-outline-secondary"
                  @click="showBookingModal = false"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { authService } from '../services/auth'
import { parkingService } from '../services/parking'

export default {
  name: 'UserDashboard',
  setup() {
    const isLoading = ref(false)
    const currentDateTime = ref('')
    const showBookingModal = ref(false)
    
    // Data
    const parkingLots = ref([])
    const reservations = ref([])
    const selectedLot = ref(null)
    
    // Form
    const bookingForm = ref({
      vehicle_number: ''
    })

    // Computed
    const currentUser = computed(() => authService.getCurrentUser())
    const activeReservations = computed(() => 
      reservations.value.filter(r => r.is_active)
    )
    const totalReservations = computed(() => reservations.value)
    const recentReservations = computed(() => 
      reservations.value.slice(0, 10)
    )

    // Methods
    const updateDateTime = () => {
      currentDateTime.value = new Date().toLocaleString()
    }

    const loadParkingLots = async () => {
      isLoading.value = true
      try {
        const result = await parkingService.getAllParkingLots()
        if (result.success) {
          parkingLots.value = result.data
        } else {
          window.showToast(result.message, 'error')
        }
      } catch (error) {
        window.showToast('Failed to load parking lots', 'error')
      } finally {
        isLoading.value = false
      }
    }

    const loadReservations = async () => {
      isLoading.value = true
      try {
        const result = await parkingService.getUserReservations()
        if (result.success) {
          reservations.value = result.data
        } else {
          window.showToast(result.message, 'error')
        }
      } catch (error) {
        window.showToast('Failed to load reservations', 'error')
      } finally {
        isLoading.value = false
      }
    }

    const selectLot = (lot) => {
      if (activeReservations.value.length > 0) {
        window.showToast('You already have an active reservation', 'warning')
        return
      }
      
      if (lot.available_spots_count === 0) {
        window.showToast('No available spots in this lot', 'warning')
        return
      }
      
      selectedLot.value = lot
      showBookingModal.value = true
    }

    const bookSpot = async () => {
      if (!bookingForm.value.vehicle_number) {
        window.showToast('Please enter vehicle number', 'error')
        return
      }

      isLoading.value = true
      try {
        const result = await parkingService.createReservation({
          lot_id: selectedLot.value.id,
          vehicle_number: bookingForm.value.vehicle_number
        })

        if (result.success) {
          window.showToast('Parking spot booked successfully!', 'success')
          showBookingModal.value = false
          selectedLot.value = null
          bookingForm.value.vehicle_number = ''
          await Promise.all([loadReservations(), loadParkingLots()])
        } else {
          window.showToast(result.message, 'error')
        }
      } catch (error) {
        window.showToast('Failed to book parking spot', 'error')
      } finally {
        isLoading.value = false
      }
    }

    const releaseSpot = async (reservationId) => {
      if (!confirm('Are you sure you want to release this parking spot?')) {
        return
      }

      isLoading.value = true
      try {
        const result = await parkingService.releaseReservation(reservationId)
        if (result.success) {
          window.showToast('Parking spot released successfully!', 'success')
          await Promise.all([loadReservations(), loadParkingLots()])
        } else {
          window.showToast(result.message, 'error')
        }
      } catch (error) {
        window.showToast('Failed to release parking spot', 'error')
      } finally {
        isLoading.value = false
      }
    }

    const getParkingLotName = (spotId) => {
      // This would need to be enhanced to map spot to lot
      return 'Parking Lot'
    }

    const formatDateTime = (datetime) => {
      return new Date(datetime).toLocaleString()
    }

    // Lifecycle
    onMounted(() => {
      updateDateTime()
      setInterval(updateDateTime, 1000)
      loadParkingLots()
      loadReservations()
    })

    return {
      isLoading,
      currentDateTime,
      showBookingModal,
      parkingLots,
      reservations,
      selectedLot,
      bookingForm,
      currentUser,
      activeReservations,
      totalReservations,
      recentReservations,
      loadParkingLots,
      loadReservations,
      selectLot,
      bookSpot,
      releaseSpot,
      getParkingLotName,
      formatDateTime
    }
  }
}
</script>

<style scoped>
.user-dashboard {
  min-height: 100vh;
  background: rgba(255, 255, 255, 0.05);
}

.stat-card {
  transition: transform 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-5px);
}

.reservation-item,
.lot-item {
  transition: all 0.3s ease;
}

.reservation-item:hover,
.lot-item:hover {
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.cursor-pointer {
  cursor: pointer;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
  padding: 2rem;
  animation: slideInUp 0.3s ease-out;
}

.btn-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
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
  .user-dashboard {
    padding: 1rem;
  }
  
  .modal-content {
    width: 95%;
    padding: 1.5rem;
  }
}
</style>