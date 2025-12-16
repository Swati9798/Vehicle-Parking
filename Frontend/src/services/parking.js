import apiClient from './api.js'

class ParkingService {  // Get user's reservations
  async getUserReservations() {
    try {
      const response = await apiClient.get('/reservations')
      return { success: true, data: response.data.data }
    } catch (error) {
      console.error('Get user reservations error:', error)
      return {
        success: false,
        message: error.response?.data?.message || 'Failed to fetch reservations'
      }
    }
  }

  // Get user summary for dashboard
  async getUserSummary() {
    try {
      const response = await apiClient.get('/user/summary')
      return { success: true, data: response.data.data }
    } catch (error) {
      console.error('Get user summary error:', error)
      return {
        success: false,
        message: error.response?.data?.message || 'Failed to fetch user summary'
      }
    }
  }

  // User search functionality (parking lots and spots)
  async search(searchQuery, searchType = 'lots') {
    try {
      const response = await apiClient.get(`/search?query=${encodeURIComponent(searchQuery)}&type=${encodeURIComponent(searchType)}`)
      return { success: true, data: response.data.data }
    } catch (error) {
      console.error('User search error:', error)
      return {
        success: false,
        message: error.response?.data?.message || 'Search failed'
      }
    }
  }

  // Get all parking lots
  async getAllParkingLots() {
    try {
      const response = await apiClient.get('/parking-lots')
      return { success: true, data: response.data.data }
    } catch (error) {
      console.error('Get parking lots error:', error)
      return {
        success: false,
        message: error.response?.data?.message || 'Failed to fetch parking lots'
      }
    }
  }

  // Get parking lot by ID with spots
  async getParkingLotById(lotId) {
    try {
      const response = await apiClient.get(`/parking-lots/${lotId}`)
      return { success: true, data: response.data.data }
    } catch (error) {
      console.error('Get parking lot error:', error)
      return {
        success: false,
        message: error.response?.data?.message || 'Failed to fetch parking lot'
      }
    }
  }

  // Create parking reservation
  async createReservation(reservationData) {
    try {
      const response = await apiClient.post('/reservations', reservationData)
      return { success: true, data: response.data.data }
    } catch (error) {
      console.error('Create reservation error:', error)
      return {
        success: false,
        message: error.response?.data?.message || 'Failed to create reservation'
      }
    }
  }

  // Release parking spot
  async releaseReservation(reservationId) {
    try {
      const response = await apiClient.put(`/reservations/${reservationId}/release`)
      return { success: true, data: response.data.data }
    } catch (error) {
      console.error('Release reservation error:', error)
      return {
        success: false,
        message: error.response?.data?.message || 'Failed to release parking spot'
      }
    }
  }

  // Get user reservations
  async getUserReservations() {
    try {
      const response = await apiClient.get('/reservations')
      return { success: true, data: response.data.data }
    } catch (error) {
      console.error('Get reservations error:', error)
      return {
        success: false,
        message: error.response?.data?.message || 'Failed to fetch reservations'
      }
    }
  }
}

class AdminService {
  // Get all parking lots (for admin)
  async getAllParkingLots() {
    try {
      const response = await apiClient.get('/parking-lots')
      return { success: true, data: response.data.data }
    } catch (error) {
      console.error('Get parking lots error:', error)
      return {
        success: false,
        message: error.response?.data?.message || 'Failed to fetch parking lots'
      }
    }
  }
  async getDashboardData() {
    try {
      const response = await apiClient.get('/admin/dashboard')
      return { success: true, data: response.data.data }
    } catch (error) {
      console.error('Get dashboard data error:', error)
      return {
        success: false,
        message: error.response?.data?.message || 'Failed to fetch dashboard data'
      }
    }
  }

  // Create parking lot
  async createParkingLot(lotData) {
    try {
      const response = await apiClient.post('/admin/parking-lots', lotData)
      return { success: true, data: response.data.data }
    } catch (error) {
      console.error('Create parking lot error:', error)
      return {
        success: false,
        message: error.response?.data?.message || 'Failed to create parking lot'
      }
    }
  }

  // Update parking lot
  async updateParkingLot(lotId, lotData) {
    try {
      const response = await apiClient.put(`/admin/parking-lots/${lotId}`, lotData)
      return { success: true, data: response.data.data }
    } catch (error) {
      console.error('Update parking lot error:', error)
      return {
        success: false,
        message: error.response?.data?.message || 'Failed to update parking lot'
      }
    }
  }

  // Delete parking lot
  async deleteParkingLot(lotId) {
    try {
      const response = await apiClient.delete(`/admin/parking-lots/${lotId}`)
      return { success: true, data: response.data }
    } catch (error) {
      console.error('Delete parking lot error:', error)
      return {
        success: false,
        message: error.response?.data?.message || 'Failed to delete parking lot'
      }
    }
  }

  // Get all users
  async getAllUsers() {
    try {
      const response = await apiClient.get('/admin/users')
      return { success: true, data: response.data.data }
    } catch (error) {
      console.error('Get users error:', error)
      return {
        success: false,
        message: error.response?.data?.message || 'Failed to fetch users'
      }
    }
  }

  // Get all reservations
  async getAllReservations() {
    try {
      const response = await apiClient.get('/admin/reservations')
      return { success: true, data: response.data.data }
    } catch (error) {
      console.error('Get reservations error:', error)
      return {
        success: false,
        message: error.response?.data?.message || 'Failed to fetch reservations'
      }
    }
  }

  // Search functionality
  async search(searchType, searchQuery) {
    try {
      const response = await apiClient.get(`/admin/search?type=${searchType}&query=${encodeURIComponent(searchQuery)}`)
      return { success: true, data: response.data.data }
    } catch (error) {
      console.error('Search error:', error)
      return {
        success: false,
        message: error.response?.data?.message || 'Search failed'
      }
    }
  }

  // Get summary data for analytics
  async getSummaryData() {
    try {
      const response = await apiClient.get('/admin/summary')
      return { success: true, data: response.data.data }
    } catch (error) {
      console.error('Get summary data error:', error)
      return {
        success: false,
        message: error.response?.data?.message || 'Failed to fetch summary data'
      }
    }
  }
}

export const parkingService = new ParkingService()
export const adminService = new AdminService()