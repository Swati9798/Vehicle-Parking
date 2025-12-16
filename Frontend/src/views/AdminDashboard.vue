<template>
  <div class="admin-dashboard">
    <div class="container-fluid py-4">
      <!-- Admin Header -->
      <div class="row mb-4">
        <div class="col-12">
          <div class="admin-header custom-card p-4">
            <div class="row align-items-center">
              <div class="col-md-8">
                <h1 class="fw-bold mb-2">
                  <i class="bi bi-shield-check text-warning me-2"></i>
                  Admin Dashboard
                </h1>
                <p class="text-muted mb-0">Manage parking lots, users, and system overview</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Statistics Cards -->
      <div class="row mb-4">
        <div class="col-lg-3 col-md-6 mb-3">
          <div class="stat-card custom-card p-4 text-center h-100">
            <i class="bi bi-building text-primary display-4"></i>
            <h3 class="fw-bold mt-2">{{ dashboardData.total_lots || 0 }}</h3>
            <p class="text-muted mb-0">Total Parking Lots</p>
          </div>
        </div>
        <div class="col-lg-3 col-md-6 mb-3">
          <div class="stat-card custom-card p-4 text-center h-100">
            <i class="bi bi-grid text-info display-4"></i>
            <h3 class="fw-bold mt-2">{{ dashboardData.total_spots || 0 }}</h3>
            <p class="text-muted mb-0">Total Parking Spots</p>
          </div>
        </div>
        <div class="col-lg-3 col-md-6 mb-3">
          <div class="stat-card custom-card p-4 text-center h-100">
            <i class="bi bi-check-circle text-success display-4"></i>
            <h3 class="fw-bold mt-2">{{ dashboardData.available_spots || 0 }}</h3>
            <p class="text-muted mb-0">Available Spots</p>
          </div>
        </div>
        <div class="col-lg-3 col-md-6 mb-3">
          <div class="stat-card custom-card p-4 text-center h-100">
            <i class="bi bi-person-fill text-warning display-4"></i>
            <h3 class="fw-bold mt-2">{{ dashboardData.total_users || 0 }}</h3>
            <p class="text-muted mb-0">Registered Users</p>
          </div>
        </div>
      </div>

      <!-- Tabs Navigation -->
      <div class="row">
        <div class="col-12">
          <div class="tabs-container custom-card p-4">
            <ul class="nav nav-pills mb-4" role="tablist">
              <li class="nav-item">
                <button 
                  class="nav-link"
                  :class="{ active: activeTab === 'lots' }"
                  @click="activeTab = 'lots'"
                >
                  <i class="bi bi-building me-2"></i>Parking Lots
                </button>
              </li>
              <li class="nav-item">
                <button 
                  class="nav-link"
                  :class="{ active: activeTab === 'reservations' }"
                  @click="activeTab = 'reservations'"
                >
                  <i class="bi bi-bookmark-check me-2"></i>Reservations
                </button>
              </li>
              <li class="nav-item">
                <button 
                  class="nav-link"
                  :class="{ active: activeTab === 'users' }"
                  @click="activeTab = 'users'"
                >
                  <i class="bi bi-people me-2"></i>Users
                </button>
              </li>
            </ul>

            <!-- Parking Lots Tab -->
            <div v-if="activeTab === 'lots'" class="tab-content">
              <div class="d-flex justify-content-between align-items-center mb-3">
                <h5 class="fw-bold mb-0">Parking Lots Management</h5>
                <button class="btn btn-success" @click="showCreateLotModal = true">
                  <i class="bi bi-plus-circle me-2"></i>Add New Lot
                </button>
              </div>

              <div v-if="parkingLots.length === 0" class="text-center py-5">
                <i class="bi bi-building text-muted display-3"></i>
                <p class="text-muted mt-3">No parking lots found</p>
                <button class="btn btn-primary" @click="showCreateLotModal = true">
                  Create First Parking Lot
                </button>
              </div>

              <div v-else class="table-responsive">
                <table class="table table-hover">
                  <thead class="table-light">
                    <tr>
                      <th>ID</th>
                      <th>Location Name</th>
                      <th>Address</th>
                      <th>Pin Code</th>
                      <th>Price/Hour</th>
                      <th>Total Spots</th>
                      <th>Available</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="lot in parkingLots" :key="lot.id">
                      <td>{{ lot.id }}</td>
                      <td>{{ lot.prime_location_name }}</td>
                      <td>{{ lot.address }}</td>
                      <td>{{ lot.pin_code }}</td>
                      <td>${{ lot.price_per_hour }}</td>
                      <td>{{ lot.number_of_spots }}</td>
                      <td>
                        <span class="badge bg-success">{{ lot.available_spots_count || 0 }}</span>
                      </td>
                      <td>
                        <button class="btn btn-outline-primary btn-sm me-1" @click="editLot(lot)">
                          <i class="bi bi-pencil"></i>
                        </button>
                        <button class="btn btn-outline-danger btn-sm" @click="deleteLot(lot.id)">
                          <i class="bi bi-trash"></i>
                        </button>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            <!-- Reservations Tab -->
            <div v-if="activeTab === 'reservations'" class="tab-content">
              <div class="d-flex justify-content-between align-items-center mb-3">
                <h5 class="fw-bold mb-0">Reservations Management</h5>
                
              </div>

              <div v-if="reservations.length === 0" class="text-center py-5">
                <i class="bi bi-bookmark-check text-muted display-3"></i>
                <p class="text-muted mt-3">No reservations found</p>
              </div>

              <div v-else class="table-responsive">
                <table class="table table-hover">
                  <thead class="table-light">
                    <tr>
                      <th>ID</th>
                      <th>User</th>
                      <th>Spot ID</th>
                      <th>Vehicle</th>
                      <th>Check-in</th>
                      <th>Check-out</th>
                      <th>Duration</th>
                      <th>Cost</th>
                      <th>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="reservation in reservations" :key="reservation.id">
                      <td>{{ reservation.id }}</td>
                      <td>{{ reservation.user_id }}</td>
                      <td>{{ reservation.spot_id }}</td>
                      <td>{{ reservation.vehicle_number || '-' }}</td>
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

            <!-- Users Tab -->
            <div v-if="activeTab === 'users'" class="tab-content">
              <div class="d-flex justify-content-between align-items-center mb-3">
                <h5 class="fw-bold mb-0">Users Management</h5>
                
              </div>

              <div v-if="users.length === 0" class="text-center py-5">
                <i class="bi bi-people text-muted display-3"></i>
                <p class="text-muted mt-3">No users found</p>
              </div>

              <div v-else class="table-responsive">
                <table class="table table-hover">
                  <thead class="table-light">
                    <tr>
                      <th>ID</th>
                      <th>Username</th>
                      <th>Email</th>
                      <th>Role</th>
                      <th>Status</th>
                      <th>Created</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="user in users" :key="user.id">
                      <td>{{ user.id }}</td>
                      <td>{{ user.username }}</td>
                      <td>{{ user.email }}</td>
                      <td>
                        <span :class="['badge', user.role === 'admin' ? 'bg-warning' : 'bg-primary']">
                          {{ user.role }}
                        </span>
                      </td>
                      <td>
                        <span :class="['badge', user.is_active ? 'bg-success' : 'bg-danger']">
                          {{ user.is_active ? 'Active' : 'Inactive' }}
                        </span>
                      </td>
                      <td>{{ formatDateTime(user.created_at) }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>


          </div>
        </div>
      </div>
    </div>

    <!-- Create/Edit Parking Lot Modal -->
    <div v-if="showCreateLotModal || showEditLotModal" class="modal-overlay" @click="closeModals">
      <div class="modal-content custom-card" @click.stop>
        <div class="modal-header border-bottom pb-3 mb-3">
          <h5 class="fw-bold mb-0">
            {{ editingLot ? 'Edit Parking Lot' : 'Create New Parking Lot' }}
          </h5>
          <button class="btn-close" @click="closeModals"></button>
        </div>
        
        <div class="modal-body">
          <form @submit.prevent="editingLot ? updateLot() : createLot()">
            <div class="row">
              <div class="col-md-6 mb-3">
                <label class="form-label fw-bold">Location Name</label>
                <input 
                  type="text" 
                  class="form-control"
                  v-model="lotForm.prime_location_name"
                  placeholder="Enter location name"
                  required
                >
              </div>
              <div class="col-md-6 mb-3">
                <label class="form-label fw-bold">Pin Code</label>
                <input 
                  type="text" 
                  class="form-control"
                  v-model="lotForm.pin_code"
                  placeholder="Enter pin code"
                  required
                >
              </div>
            </div>
            
            <div class="mb-3">
              <label class="form-label fw-bold">Address</label>
              <textarea 
                class="form-control"
                v-model="lotForm.address"
                rows="3"
                placeholder="Enter full address"
                required
              ></textarea>
            </div>
            
            <div class="row">
              <div class="col-md-6 mb-3">
                <label class="form-label fw-bold">Price per Hour ($)</label>
                <input 
                  type="number" 
                  class="form-control"
                  v-model="lotForm.price_per_hour"
                  step="0.01"
                  min="0"
                  placeholder="0.00"
                  required
                >
              </div>
              <div class="col-md-6 mb-3">
                <label class="form-label fw-bold">Number of Spots</label>
                <input 
                  type="number" 
                  class="form-control"
                  v-model="lotForm.number_of_spots"
                  min="1"
                  placeholder="Enter number of spots"
                  required
                >
              </div>
            </div>
            
            <div class="d-grid gap-2">
              <button 
                type="submit" 
                class="btn btn-gradient"
                :disabled="isLoading"
              >
                <span v-if="isLoading" class="spinner-border spinner-border-sm me-2"></span>
                <i v-else class="bi bi-check-circle me-2"></i>
                {{ isLoading ? 'Saving...' : (editingLot ? 'Update Lot' : 'Create Lot') }}
              </button>
              <button 
                type="button" 
                class="btn btn-outline-secondary"
                @click="closeModals"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, watch } from 'vue'
import { adminService } from '../services/parking'

export default {
  name: 'AdminDashboard',
  setup() {
    const isLoading = ref(false)
    const activeTab = ref('lots')
    const showCreateLotModal = ref(false)
    const showEditLotModal = ref(false)
    const editingLot = ref(null)
    
    // Data
    const dashboardData = ref({})
    const parkingLots = ref([])
    const reservations = ref([])
    const users = ref([])
    
    // Form
    const lotForm = ref({
      prime_location_name: '',
      address: '',
      pin_code: '',
      price_per_hour: '',
      number_of_spots: ''
    })

    // Watch for tab changes and load data automatically
    watch(activeTab, (newTab) => {
      if (newTab === 'reservations' && reservations.value.length === 0) {
        loadReservations()
      } else if (newTab === 'users' && users.value.length === 0) {
        loadUsers()
      }
    })

    // Methods
    const loadDashboardData = async () => {
      isLoading.value = true
      try {
        const result = await adminService.getDashboardData()
        if (result.success) {
          dashboardData.value = result.data
        } else {
          window.showToast(result.message, 'error')
        }
      } catch (error) {
        window.showToast('Failed to load dashboard data', 'error')
      } finally {
        isLoading.value = false
      }
    }

    const loadParkingLots = async () => {
      try {
        const result = await adminService.getAllParkingLots()
        if (result.success) {
          parkingLots.value = result.data
        }
      } catch (error) {
        window.showToast('Failed to load parking lots', 'error')
      }
    }

    const loadReservations = async () => {
      try {
        const result = await adminService.getAllReservations()
        if (result.success) {
          reservations.value = result.data
        }
      } catch (error) {
        window.showToast('Failed to load reservations', 'error')
      }
    }

    const loadUsers = async () => {
      try {
        const result = await adminService.getAllUsers()
        if (result.success) {
          users.value = result.data
        }
      } catch (error) {
        window.showToast('Failed to load users', 'error')
      }
    }

    const createLot = async () => {
      isLoading.value = true
      try {
        const result = await adminService.createParkingLot(lotForm.value)
        if (result.success) {
          window.showToast('Parking lot created successfully!', 'success')
          closeModals()
          resetForm()
          await Promise.all([loadDashboardData(), loadParkingLots()])
        } else {
          window.showToast(result.message, 'error')
        }
      } catch (error) {
        window.showToast('Failed to create parking lot', 'error')
      } finally {
        isLoading.value = false
      }
    }

    const editLot = (lot) => {
      editingLot.value = lot
      lotForm.value = { ...lot }
      showEditLotModal.value = true
    }

    const updateLot = async () => {
      isLoading.value = true
      try {
        const result = await adminService.updateParkingLot(editingLot.value.id, lotForm.value)
        if (result.success) {
          window.showToast('Parking lot updated successfully!', 'success')
          closeModals()
          resetForm()
          await Promise.all([loadDashboardData(), loadParkingLots()])
        } else {
          window.showToast(result.message, 'error')
        }
      } catch (error) {
        window.showToast('Failed to update parking lot', 'error')
      } finally {
        isLoading.value = false
      }
    }

    const deleteLot = async (lotId) => {
      if (!confirm('Are you sure you want to delete this parking lot?')) {
        return
      }

      isLoading.value = true
      try {
        const result = await adminService.deleteParkingLot(lotId)
        if (result.success) {
          window.showToast('Parking lot deleted successfully!', 'success')
          await Promise.all([loadDashboardData(), loadParkingLots()])
        } else {
          window.showToast(result.message, 'error')
        }
      } catch (error) {
        window.showToast('Failed to delete parking lot', 'error')
      } finally {
        isLoading.value = false
      }
    }

    const closeModals = () => {
      showCreateLotModal.value = false
      showEditLotModal.value = false
      editingLot.value = null
      resetForm()
    }

    const resetForm = () => {
      lotForm.value = {
        prime_location_name: '',
        address: '',
        pin_code: '',
        price_per_hour: '',
        number_of_spots: ''
      }
    }

    const formatDateTime = (datetime) => {
      return new Date(datetime).toLocaleString()
    }

    // Lifecycle
    onMounted(async () => {
      await loadDashboardData()
      await loadParkingLots()
      await loadReservations() // Load reservations on initial load
      await loadUsers()        // Load users on initial load
    })

    return {
      isLoading,
      activeTab,
      showCreateLotModal,
      showEditLotModal,
      editingLot,
      dashboardData,
      parkingLots,
      reservations,
      users,
      lotForm,
      // Methods
      loadDashboardData,
      loadParkingLots,
      loadReservations,
      loadUsers,
      createLot,
      editLot,
      updateLot,
      deleteLot,
      closeModals,
      formatDateTime
    }
  }
}
</script>

<style scoped>
.admin-dashboard {
  min-height: 100vh;
  background: rgba(255, 255, 255, 0.05);
}

.stat-card {
  transition: transform 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-5px);
}

.nav-pills .nav-link {
  color: #666;
  background: rgba(102, 126, 234, 0.1);
  margin-right: 0.5rem;
  border-radius: 25px;
  transition: all 0.3s ease;
}

.nav-pills .nav-link.active {
  background: linear-gradient(45deg, #667eea, #764ba2);
  color: white;
}

.nav-pills .nav-link:hover:not(.active) {
  background: rgba(102, 126, 234, 0.2);
  color: #667eea;
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
  max-width: 600px;
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
  .admin-dashboard {
    padding: 1rem;
  }
  
  .modal-content {
    width: 95%;
    padding: 1.5rem;
  }
  
  .nav-pills {
    flex-direction: column;
  }
  
  .nav-pills .nav-link {
    margin-bottom: 0.5rem;
    margin-right: 0;
  }
}
</style>