<template>
  <div class="search-page">
    <div class="container">
      <div class="row justify-content-center">
        <div class="col-12">
          <div class="search-container custom-card p-4">
            <h2 class="fw-bold mb-4 text-center">
              <i class="bi bi-search me-2"></i>Search Dashboard
            </h2>
            
            <!-- Navigation Button -->
            <div class="row mb-3">
              <div class="col-12">
                <button class="btn btn-outline-secondary" @click="goToDashboard">
                  <i class="bi bi-arrow-left me-2"></i>Back to Dashboard
                </button>
              </div>
            </div>
            
            <!-- Search Controls -->
            <div class="row mb-4">
              <div class="col-md-8">
                <div class="input-group">
                  <select v-if="currentUser && currentUser.role === 'admin'" class="form-select" v-model="searchType" style="max-width: 200px;">
                    <option value="user_id">User ID</option>
                    <option value="username">Username</option>
                    <option value="spot_location">Spot by Location</option>
                    <option value="lot_location">Parking Lot by Location</option>
                  </select>
                  <select v-else class="form-select" v-model="userSearchType" style="max-width: 200px;">
                    <option value="lots">Parking Lots</option>
                    <option value="spots">Parking Spots</option>
                  </select>
                  <input 
                    type="text" 
                    class="form-control" 
                    v-model="searchQuery"
                    :placeholder="getSearchPlaceholder()"
                    @keyup.enter="performSearch"
                  >
                  <button class="btn btn-primary" @click="performSearch" :disabled="isLoading">
                    <i class="bi bi-search"></i> Search
                  </button>
                </div>
              </div>
              <div class="col-md-4">
                <button class="btn btn-outline-secondary" @click="clearSearch">
                  <i class="bi bi-x-circle"></i> Clear
                </button>
              </div>
            </div>

            <!-- Loading State -->
            <div v-if="isLoading" class="text-center py-5">
              <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
              <p class="mt-2">Searching...</p>
            </div>

            <!-- Search Results -->
            <div v-else-if="searchResults.length > 0" class="search-results">
              <h5 class="fw-bold mb-3">Search Results ({{ searchResults.length }})</h5>
              
              <!-- User Results -->
              <div v-if="searchType === 'user_id' || searchType === 'username'" class="table-responsive">
                <table class="table table-hover">
                  <thead class="table-light">
                    <tr>
                      <th>ID</th>
                      <th>Username</th>
                      <th>Email</th>
                      <th>Role</th>
                      <th>Status</th>
                      <th>Total Reservations</th>
                      <th>Created</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="result in searchResults" :key="result.id">
                      <td>{{ result.id }}</td>
                      <td>{{ result.username }}</td>
                      <td>{{ result.email }}</td>
                      <td>
                        <span :class="['badge', result.role === 'admin' ? 'bg-warning' : 'bg-primary']">
                          {{ result.role }}
                        </span>
                      </td>
                      <td>
                        <span :class="['badge', result.is_active ? 'bg-success' : 'bg-danger']">
                          {{ result.is_active ? 'Active' : 'Inactive' }}
                        </span>
                      </td>
                      <td>{{ result.total_reservations || 0 }}</td>
                      <td>{{ formatDateTime(result.created_at) }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>

              <!-- Parking Lot Results -->
              <div v-else-if="searchType === 'lot_location'" class="table-responsive">
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
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="result in searchResults" :key="result.id">
                      <td>{{ result.id }}</td>
                      <td>{{ result.prime_location_name }}</td>
                      <td>{{ result.address }}</td>
                      <td>{{ result.pin_code }}</td>
                      <td>${{ result.price_per_hour }}</td>
                      <td>{{ result.number_of_spots }}</td>
                      <td>
                        <span class="badge bg-success">{{ result.available_spots_count || 0 }}</span>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>

              <!-- Spot Results -->
              <div v-else-if="searchType === 'spot_location'" class="table-responsive">
                <table class="table table-hover">
                  <thead class="table-light">
                    <tr>
                      <th>Spot ID</th>
                      <th>Parking Lot</th>
                      <th>Location</th>
                      <th>Status</th>
                      <th>Current User</th>
                      <th>Reserved Since</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="result in searchResults" :key="result.id">
                      <td>{{ result.id }}</td>
                      <td>{{ result.lot_name }}</td>
                      <td>{{ result.location }}</td>
                      <td>
                        <span :class="['badge', result.is_available ? 'bg-success' : 'bg-danger']">
                          {{ result.is_available ? 'Available' : 'Occupied' }}
                        </span>
                      </td>
                      <td>{{ result.current_user || '-' }}</td>
                      <td>{{ result.reserved_since ? formatDateTime(result.reserved_since) : '-' }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>

              <!-- User Search Results for Lots -->
              <div v-else-if="userSearchType === 'lots'" class="table-responsive">
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
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="result in searchResults" :key="result.id">
                      <td>{{ result.id }}</td>
                      <td>{{ result.prime_location_name }}</td>
                      <td>{{ result.address }}</td>
                      <td>{{ result.pin_code }}</td>
                      <td>${{ result.price_per_hour }}</td>
                      <td>{{ result.number_of_spots }}</td>
                      <td>
                        <span class="badge bg-success">{{ result.available_spots_count || 0 }}</span>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>

              <!-- User Search Results for Spots -->
              <div v-else-if="userSearchType === 'spots'" class="table-responsive">
                <table class="table table-hover">
                  <thead class="table-light">
                    <tr>
                      <th>Spot ID</th>
                      <th>Spot Number</th>
                      <th>Location Name</th>
                      <th>Address</th>
                      <th>Price/Hour</th>
                      <th>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="result in searchResults" :key="result.id">
                      <td>{{ result.id }}</td>
                      <td>{{ result.spot_number }}</td>
                      <td>{{ result.prime_location_name }}</td>
                      <td>{{ result.address }}</td>
                      <td>${{ result.price_per_hour }}</td>
                      <td>
                        <span :class="['badge', result.is_available ? 'bg-success' : 'bg-danger']">
                          {{ result.is_available ? 'Available' : 'Occupied' }}
                        </span>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            <!-- No Results -->
            <div v-else-if="searchPerformed && searchResults.length === 0" class="text-center py-5">
              <i class="bi bi-search text-muted display-3"></i>
              <p class="text-muted mt-3">No results found for "{{ searchQuery }}"</p>
              <p class="text-muted">Try adjusting your search criteria</p>
            </div>

            <!-- Initial State -->
            <div v-else class="text-center py-5">
              <i class="bi bi-search text-muted display-3"></i>
              <p class="text-muted mt-3">Enter search criteria and click search</p>
              <p class="text-muted">You can search by User ID, Username, or Location</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { authService } from '../services/auth'
import { adminService, parkingService } from '../services/parking'

export default {
  name: 'Search',
  setup() {
    const router = useRouter()
    const isLoading = ref(false)
    const searchType = ref('lot_location') // Default to location search for regular users
    const userSearchType = ref('lots') // New: For regular users to choose between lots and spots
    const searchQuery = ref('')
    const searchResults = ref([])
    const searchPerformed = ref(false)
    const currentUser = ref(authService.getCurrentUser())

    // Check authentication
    if (!authService.isAuthenticated()) {
      router.push('/login')
    }

    // Set appropriate default search type based on user role
    if (currentUser.value && currentUser.value.role === 'admin') {
      searchType.value = 'user_id'
    }

    const getSearchPlaceholder = () => {
      // For regular users, show different placeholders based on userSearchType
      if (!currentUser.value || currentUser.value.role !== 'admin') {
        const userPlaceholders = {
          lots: 'Enter location to find parking lots (e.g., Downtown, Airport)',
          spots: 'Enter location or spot number to find parking spots'
        }
        return userPlaceholders[userSearchType.value] || 'Enter search term'
      }
      
      // For admins, show different placeholders based on search type
      const placeholders = {
        user_id: 'Enter User ID (e.g., 1, 2, 3)',
        username: 'Enter Username (e.g., john_doe)',
        spot_location: 'Enter Location (e.g., Downtown, Mall)',
        lot_location: 'Enter Location (e.g., Downtown, Airport)'
      }
      return placeholders[searchType.value] || 'Enter search term'
    }

    const performSearch = async () => {
      if (!searchQuery.value.trim()) {
        alert('Please enter a search term')
        return
      }

      try {
        isLoading.value = true
        searchPerformed.value = true
        
        // Use appropriate service based on user role
        const user = authService.getCurrentUser()
        let result
        
        if (user && user.role === 'admin') {
          result = await adminService.search(searchType.value, searchQuery.value)
        } else {
          // Regular users can search for parking lots or spots
          result = await parkingService.search(searchQuery.value, userSearchType.value)
        }
        
        if (result.success) {
          searchResults.value = result.data || []
        } else {
          searchResults.value = []
          alert(result.message || 'Search failed')
        }
      } catch (error) {
        console.error('Search error:', error)
        searchResults.value = []
        alert('Search failed. Please try again.')
      } finally {
        isLoading.value = false
      }
    }

    const clearSearch = () => {
      searchQuery.value = ''
      searchResults.value = []
      searchPerformed.value = false
    }

    const goToDashboard = () => {
      // Navigate to appropriate dashboard based on user role
      if (currentUser.value && currentUser.value.role === 'admin') {
        router.push('/admin')
      } else {
        router.push('/dashboard')
      }
    }

    const formatDateTime = (datetime) => {
      if (!datetime) return '-'
      return new Date(datetime).toLocaleString()
    }

    return {
      isLoading,
      searchType,
      userSearchType,
      searchQuery,
      searchResults,
      searchPerformed,
      currentUser,
      getSearchPlaceholder,
      performSearch,
      clearSearch,
      goToDashboard,
      formatDateTime
    }
  }
}
</script>

<style scoped>
.search-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 2rem 0;
}

.search-container {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.custom-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 15px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.table {
  background: white;
  border-radius: 10px;
  overflow: hidden;
}

.btn {
  border-radius: 10px;
  font-weight: 600;
  transition: all 0.3s ease;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
}

.form-control, .form-select {
  border-radius: 10px;
  border: 2px solid #e9ecef;
  transition: all 0.3s ease;
}

.form-control:focus, .form-select:focus {
  border-color: #667eea;
  box-shadow: 0 0 0 0.2rem rgba(102, 126, 234, 0.25);
}

@media (max-width: 768px) {
  .search-page {
    padding: 1rem;
  }
  
  .input-group {
    flex-direction: column;
  }
  
  .input-group .form-select,
  .input-group .form-control,
  .input-group .btn {
    margin-bottom: 0.5rem;
    border-radius: 10px !important;
  }
}
</style>