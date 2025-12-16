<template>
  <div class="summary-page">
    <div class="container">
      <div class="row justify-content-center">
        <div class="col-12">
          <div class="summary-container custom-card p-4">
            <h2 class="fw-bold mb-4 text-center">
              <i class="bi bi-graph-up me-2"></i>{{ isAdmin() ? 'Admin' : 'User' }} Summary Dashboard
            </h2>

            <!-- Navigation Button -->
            <div class="row mb-3">
              <div class="col-12">
                <button class="btn btn-outline-secondary" @click="goToDashboard">
                  <i class="bi bi-arrow-left me-2"></i>Back to Dashboard
                </button>
              </div>
            </div>

            <!-- Loading State -->
            <div v-if="isLoading" class="text-center py-5">
              <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
              <p class="mt-2">Loading summary data...</p>
            </div>

            <!-- Admin Summary -->
            <div v-else-if="isAdmin()" class="admin-summary">
              <!-- Revenue Summary -->
              <div class="row mb-4">
                <div class="col-md-3">
                  <div class="stat-card custom-card p-3 text-center">
                    <i class="bi bi-currency-dollar text-success display-4"></i>
                    <h4 class="fw-bold mt-2">${{ summaryData.total_revenue || '0.00' }}</h4>
                    <p class="text-muted mb-0">Total Revenue</p>
                  </div>
                </div>
                <div class="col-md-3">
                  <div class="stat-card custom-card p-3 text-center">
                    <i class="bi bi-graph-up text-primary display-4"></i>
                    <h4 class="fw-bold mt-2">{{ summaryData.avg_occupancy || '0' }}%</h4>
                    <p class="text-muted mb-0">Avg Occupancy</p>
                  </div>
                </div>
                <div class="col-md-3">
                  <div class="stat-card custom-card p-3 text-center">
                    <i class="bi bi-people text-info display-4"></i>
                    <h4 class="fw-bold mt-2">{{ summaryData.active_users || '0' }}</h4>
                    <p class="text-muted mb-0">Active Users</p>
                  </div>
                </div>
                <div class="col-md-3">
                  <div class="stat-card custom-card p-3 text-center">
                    <i class="bi bi-clock text-warning display-4"></i>
                    <h4 class="fw-bold mt-2">{{ summaryData.avg_duration || '0' }}h</h4>
                    <p class="text-muted mb-0">Avg Duration</p>
                  </div>
                </div>
              </div>

              <!-- Revenue by Parking Lot -->
              <div class="row mb-4">
                <div class="col-md-6">
                  <div class="custom-card p-4">
                    <h6 class="fw-bold mb-3">Revenue by Parking Lot</h6>
                    <div class="chart-container">
                      <canvas id="revenueChart" width="400" height="200"></canvas>
                    </div>
                    <!-- Fallback table if charts don't work -->
                    <div v-if="summaryData.revenue_by_lot" class="table-responsive mt-3">
                      <table class="table table-sm">
                        <thead>
                          <tr>
                            <th>Parking Lot</th>
                            <th>Revenue</th>
                          </tr>
                        </thead>
                        <tbody>
                          <tr v-for="(revenue, lot) in summaryData.revenue_by_lot" :key="lot">
                            <td>{{ lot }}</td>
                            <td>${{ revenue }}</td>
                          </tr>
                        </tbody>
                      </table>
                    </div>
                  </div>
                </div>
                <div class="col-md-6">
                  <div class="custom-card p-4">
                    <h6 class="fw-bold mb-3">Parking Lot Occupancy</h6>
                    <div class="chart-container">
                      <canvas id="occupancyChart" width="400" height="200"></canvas>
                    </div>
                    <!-- Fallback table -->
                    <div v-if="summaryData.occupancy_by_lot" class="table-responsive mt-3">
                      <table class="table table-sm">
                        <thead>
                          <tr>
                            <th>Parking Lot</th>
                            <th>Occupied</th>
                            <th>Available</th>
                            <th>Occupancy %</th>
                          </tr>
                        </thead>
                        <tbody>
                          <tr v-for="lot in summaryData.occupancy_by_lot" :key="lot.name">
                            <td>{{ lot.name }}</td>
                            <td>{{ lot.occupied }}</td>
                            <td>{{ lot.available }}</td>
                            <td>{{ lot.occupancy_percentage }}%</td>
                          </tr>
                        </tbody>
                      </table>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Monthly Revenue Trend -->
              <div class="row">
                <div class="col-12">
                  <div class="custom-card p-4">
                    <h6 class="fw-bold mb-3">Monthly Revenue Trend</h6>
                    <div class="chart-container">
                      <canvas id="monthlyRevenueChart" width="800" height="300"></canvas>
                    </div>
                    <!-- Fallback table -->
                    <div v-if="summaryData.monthly_revenue" class="table-responsive mt-3">
                      <table class="table table-sm">
                        <thead>
                          <tr>
                            <th>Month</th>
                            <th>Revenue</th>
                            <th>Reservations</th>
                          </tr>
                        </thead>
                        <tbody>
                          <tr v-for="month in summaryData.monthly_revenue" :key="month.month">
                            <td>{{ month.month }}</td>
                            <td>${{ month.revenue }}</td>
                            <td>{{ month.reservations }}</td>
                          </tr>
                        </tbody>
                      </table>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- User Summary -->
            <div v-else class="user-summary">
              <!-- User Stats -->
              <div class="row mb-4">
                <div class="col-md-3">
                  <div class="stat-card custom-card p-3 text-center">
                    <i class="bi bi-bookmark-check text-primary display-4"></i>
                    <h4 class="fw-bold mt-2">{{ userSummary.total_reservations || '0' }}</h4>
                    <p class="text-muted mb-0">Total Reservations</p>
                  </div>
                </div>
                <div class="col-md-3">
                  <div class="stat-card custom-card p-3 text-center">
                    <i class="bi bi-currency-dollar text-success display-4"></i>
                    <h4 class="fw-bold mt-2">${{ userSummary.total_spent || '0.00' }}</h4>
                    <p class="text-muted mb-0">Total Spent</p>
                  </div>
                </div>
                <div class="col-md-3">
                  <div class="stat-card custom-card p-3 text-center">
                    <i class="bi bi-clock text-warning display-4"></i>
                    <h4 class="fw-bold mt-2">{{ userSummary.total_hours || '0' }}h</h4>
                    <p class="text-muted mb-0">Total Parking Time</p>
                  </div>
                </div>
                <div class="col-md-3">
                  <div class="stat-card custom-card p-3 text-center">
                    <i class="bi bi-geo-alt text-info display-4"></i>
                    <h4 class="fw-bold mt-2">{{ userSummary.favorite_location || 'N/A' }}</h4>
                    <p class="text-muted mb-0">Favorite Location</p>
                  </div>
                </div>
              </div>

              <!-- User's Parking History -->
              <div class="row mb-4">
                <div class="col-md-6">
                  <div class="custom-card p-4">
                    <h6 class="fw-bold mb-3">Monthly Usage</h6>
                    <div class="chart-container">
                      <canvas id="userMonthlyChart" width="400" height="200"></canvas>
                    </div>
                    <!-- Fallback table -->
                    <div v-if="userSummary.monthly_usage" class="table-responsive mt-3">
                      <table class="table table-sm">
                        <thead>
                          <tr>
                            <th>Month</th>
                            <th>Reservations</th>
                            <th>Hours</th>
                            <th>Spent</th>
                          </tr>
                        </thead>
                        <tbody>
                          <tr v-for="month in userSummary.monthly_usage" :key="month.month">
                            <td>{{ month.month }}</td>
                            <td>{{ month.reservations }}</td>
                            <td>{{ month.hours }}h</td>
                            <td>${{ month.spent }}</td>
                          </tr>
                        </tbody>
                      </table>
                    </div>
                  </div>
                </div>
                <div class="col-md-6">
                  <div class="custom-card p-4">
                    <h6 class="fw-bold mb-3">Parking Locations Used</h6>
                    <div class="chart-container">
                      <canvas id="userLocationsChart" width="400" height="200"></canvas>
                    </div>
                    <!-- Fallback table -->
                    <div v-if="userSummary.locations_used" class="table-responsive mt-3">
                      <table class="table table-sm">
                        <thead>
                          <tr>
                            <th>Location</th>
                            <th>Times Used</th>
                            <th>Total Hours</th>
                          </tr>
                        </thead>
                        <tbody>
                          <tr v-for="location in userSummary.locations_used" :key="location.name">
                            <td>{{ location.name }}</td>
                            <td>{{ location.count }}</td>
                            <td>{{ location.hours }}h</td>
                          </tr>
                        </tbody>
                      </table>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Recent Reservations -->
              <div class="row">
                <div class="col-12">
                  <div class="custom-card p-4">
                    <h6 class="fw-bold mb-3">Recent Reservations</h6>
                    <div v-if="userSummary.recent_reservations && userSummary.recent_reservations.length > 0" class="table-responsive">
                      <table class="table table-hover">
                        <thead class="table-light">
                          <tr>
                            <th>Date</th>
                            <th>Location</th>
                            <th>Duration</th>
                            <th>Cost</th>
                            <th>Status</th>
                          </tr>
                        </thead>
                        <tbody>
                          <tr v-for="reservation in userSummary.recent_reservations" :key="reservation.id">
                            <td>{{ formatDate(reservation.parking_timestamp) }}</td>
                            <td>{{ reservation.location }}</td>
                            <td>{{ reservation.duration_hours }}h</td>
                            <td>${{ reservation.parking_cost }}</td>
                            <td>
                              <span :class="['badge', reservation.is_active ? 'bg-success' : 'bg-secondary']">
                                {{ reservation.is_active ? 'Active' : 'Completed' }}
                              </span>
                            </td>
                          </tr>
                        </tbody>
                      </table>
                    </div>
                    <div v-else class="text-center py-4">
                      <i class="bi bi-bookmark text-muted display-4"></i>
                      <p class="text-muted mt-2">No reservations found</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { authService } from '../services/auth'
import { adminService, parkingService } from '../services/parking'

export default {
  name: 'Summary',
  setup() {
    const router = useRouter()
    const isLoading = ref(true)
    const summaryData = ref({})
    const userSummary = ref({})
    const charts = ref({})

    // Check authentication
    if (!authService.isAuthenticated()) {
      router.push('/login')
    }

    const isAdmin = () => {
      return authService.isAdmin()
    }

    const loadSummaryData = async () => {
      try {
        isLoading.value = true
        
        if (isAdmin()) {
          // Load admin summary
          const result = await adminService.getSummaryData()
          if (result.success) {
            summaryData.value = result.data
            // Wait for DOM and render charts
            setTimeout(() => {
              renderAdminCharts()
            }, 1000)
          } else {
            alert(result.message || 'Failed to load summary data')
          }
        } else {
          // Load user summary
          const result = await parkingService.getUserSummary()
          if (result.success) {
            userSummary.value = result.data
            // Wait for DOM and render charts
            setTimeout(() => {
              renderUserCharts()
            }, 1000)
          } else {
            alert(result.message || 'Failed to load user summary')
          }
        }
      } catch (error) {
        console.error('Failed to load summary:', error)
        alert('Failed to load summary data')
      } finally {
        isLoading.value = false
      }
    }

    const renderAdminCharts = () => {
      if (window.Chart) {
        renderRevenueChart()
        renderOccupancyChart()
        renderMonthlyRevenueChart()
      } else {
        console.error('Chart.js not available')
      }
    }

    const renderUserCharts = () => {
      if (window.Chart) {
        renderUserMonthlyChart()
        renderUserLocationsChart()
      } else {
        console.error('Chart.js not available')
      }
    }

    const renderRevenueChart = () => {
      const canvas = document.getElementById('revenueChart')
      if (!canvas || !summaryData.value.revenue_by_lot) return

      const ctx = canvas.getContext('2d')
      const revenueData = summaryData.value.revenue_by_lot
      
      if (charts.value.revenue) {
        charts.value.revenue.destroy()
      }

      charts.value.revenue = new window.Chart(ctx, {
        type: 'doughnut',
        data: {
          labels: Object.keys(revenueData),
          datasets: [{
            data: Object.values(revenueData),
            backgroundColor: ['#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe', '#00f2fe']
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false
        }
      })
    }

    const renderOccupancyChart = () => {
      const canvas = document.getElementById('occupancyChart')
      if (!canvas || !summaryData.value.occupancy_by_lot) return

      const ctx = canvas.getContext('2d')
      const occupancyData = summaryData.value.occupancy_by_lot
      
      if (charts.value.occupancy) {
        charts.value.occupancy.destroy()
      }

      charts.value.occupancy = new window.Chart(ctx, {
        type: 'bar',
        data: {
          labels: occupancyData.map(lot => lot.name),
          datasets: [{
            label: 'Occupied',
            data: occupancyData.map(lot => lot.occupied),
            backgroundColor: '#f5576c'
          }, {
            label: 'Available',
            data: occupancyData.map(lot => lot.available),
            backgroundColor: '#4facfe'
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            y: {
              beginAtZero: true
            }
          }
        }
      })
    }

    const renderMonthlyRevenueChart = () => {
      const canvas = document.getElementById('monthlyRevenueChart')
      if (!canvas || !summaryData.value.monthly_revenue) return

      const ctx = canvas.getContext('2d')
      const monthlyData = summaryData.value.monthly_revenue
      
      if (charts.value.monthlyRevenue) {
        charts.value.monthlyRevenue.destroy()
      }

      charts.value.monthlyRevenue = new window.Chart(ctx, {
        type: 'line',
        data: {
          labels: monthlyData.map(month => month.month),
          datasets: [{
            label: 'Revenue ($)',
            data: monthlyData.map(month => month.revenue),
            borderColor: '#667eea',
            backgroundColor: 'rgba(102, 126, 234, 0.1)',
            fill: true
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false
        }
      })
    }

    const renderUserMonthlyChart = () => {
      const canvas = document.getElementById('userMonthlyChart')
      if (!canvas || !userSummary.value.monthly_usage) return

      const ctx = canvas.getContext('2d')
      const monthlyData = userSummary.value.monthly_usage
      
      if (charts.value.userMonthly) {
        charts.value.userMonthly.destroy()
      }

      charts.value.userMonthly = new window.Chart(ctx, {
        type: 'bar',
        data: {
          labels: monthlyData.map(month => month.month),
          datasets: [{
            label: 'Hours',
            data: monthlyData.map(month => month.hours),
            backgroundColor: '#667eea'
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            y: {
              beginAtZero: true
            }
          }
        }
      })
    }

    const renderUserLocationsChart = () => {
      const canvas = document.getElementById('userLocationsChart')
      if (!canvas || !userSummary.value.locations_used) return

      const ctx = canvas.getContext('2d')
      const locationsData = userSummary.value.locations_used
      
      if (charts.value.userLocations) {
        charts.value.userLocations.destroy()
      }

      charts.value.userLocations = new window.Chart(ctx, {
        type: 'pie',
        data: {
          labels: locationsData.map(location => location.name),
          datasets: [{
            data: locationsData.map(location => location.count),
            backgroundColor: ['#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe', '#00f2fe']
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false
        }
      })
    }

    const formatDate = (dateString) => {
      if (!dateString) return '-'
      return new Date(dateString).toLocaleDateString()
    }

    const goToDashboard = () => {
      // Navigate to appropriate dashboard based on user role
      if (isAdmin()) {
        router.push('/admin')
      } else {
        router.push('/dashboard')
      }
    }

    onMounted(() => {
      loadSummaryData()
    })

    return {
      isLoading,
      summaryData,
      userSummary,
      isAdmin,
      formatDate,
      goToDashboard
    }
  }
}
</script>

<style scoped>
.summary-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 2rem 0;
}

.summary-container {
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
  margin-bottom: 1rem;
}

.stat-card {
  transition: transform 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-5px);
}

.chart-container {
  position: relative;
  height: 300px;
  width: 100%;
  margin-bottom: 1rem;
}

.chart-container canvas {
  max-height: 300px !important;
}

.table {
  background: white;
  border-radius: 10px;
  overflow: hidden;
}

@media (max-width: 768px) {
  .summary-page {
    padding: 1rem;
  }
  
  .row > div {
    margin-bottom: 1rem;
  }
}
</style>