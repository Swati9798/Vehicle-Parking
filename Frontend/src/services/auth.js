import apiClient from './api.js'

class AuthService {
  // Login user
  async login(credentials) {
    try {
      const response = await apiClient.post('/auth/login', credentials)
      const { access_token, refresh_token, user } = response.data.data
      
      // Store tokens and user data
      localStorage.setItem('access_token', access_token)
      localStorage.setItem('refresh_token', refresh_token)
      localStorage.setItem('user', JSON.stringify(user))
      
      return { success: true, user }
    } catch (error) {
      console.error('Login error:', error)
      return {
        success: false,
        message: error.response?.data?.message || 'Login failed'
      }
    }
  }

  // Register user
  async register(userData) {
    try {
      const response = await apiClient.post('/auth/register', userData)
      return { success: true, data: response.data }
    } catch (error) {
      console.error('Registration error:', error)
      return {
        success: false,
        message: error.response?.data?.message || 'Registration failed'
      }
    }
  }

  // Logout user
  async logout() {
    try {
      await apiClient.post('/auth/logout')
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      // Clear local storage regardless of API response
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('user')
    }
  }

  // Get current user profile
  async getProfile() {
    try {
      const response = await apiClient.get('/auth/profile')
      const user = response.data.data
      localStorage.setItem('user', JSON.stringify(user))
      return { success: true, user }
    } catch (error) {
      console.error('Get profile error:', error)
      return {
        success: false,
        message: error.response?.data?.message || 'Failed to get profile'
      }
    }
  }

  // Check if user is authenticated
  isAuthenticated() {
    const token = localStorage.getItem('access_token')
    const user = localStorage.getItem('user')
    return !!(token && user)
  }

  // Get current user data
  getCurrentUser() {
    const userStr = localStorage.getItem('user')
    return userStr ? JSON.parse(userStr) : null
  }

  // Check if current user is admin
  isAdmin() {
    const user = this.getCurrentUser()
    return user?.role === 'admin'
  }

  // Get auth token
  getToken() {
    return localStorage.getItem('access_token')
  }
}

export const authService = new AuthService()

// Export convenience functions
export const isAuthenticated = () => authService.isAuthenticated()
export const isAdmin = () => authService.isAdmin()
export const getCurrentUser = () => authService.getCurrentUser()