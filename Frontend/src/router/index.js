import { createRouter, createWebHistory } from 'vue-router'
import { isAuthenticated, isAdmin } from '../services/auth'

// Import views
import Home from '../views/Home.vue'
import Login from '../views/Login.vue'
import Register from '../views/Register.vue'
import UserDashboard from '../views/UserDashboard.vue'
import AdminDashboard from '../views/AdminDashboard.vue'
import Profile from '../views/Profile.vue'
import Search from '../views/Search.vue'
import Summary from '../views/Summary.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { requiresGuest: true }
  },
  {
    path: '/register',
    name: 'Register',
    component: Register,
    meta: { requiresGuest: true }
  },
  {
    path: '/dashboard',
    name: 'UserDashboard',
    component: UserDashboard,
    meta: { requiresAuth: true, requiresUser: true }
  },
  {
    path: '/admin',
    name: 'AdminDashboard',
    component: AdminDashboard,
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: Profile,
    meta: { requiresAuth: true }
  },
  {
    path: '/search',
    name: 'Search',
    component: Search,
    meta: { requiresAuth: true }
  },
  {
    path: '/summary',
    name: 'Summary',
    component: Summary,
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Navigation guards
router.beforeEach((to, from, next) => {
  console.log(`Navigating from ${from.path} to ${to.path}`)
  console.log('Is authenticated:', isAuthenticated())
  
  // Always allow access to landing page
  if (to.path === '/') {
    console.log('Allowing access to landing page')
    return next()
  }

  // Always allow access to login and register pages
  if (to.path === '/login' || to.path === '/register') {
    console.log('Allowing access to login/register page')
    return next()
  }

  const requiresAuth = to.meta.requiresAuth
  const requiresAdmin = to.meta.requiresAdmin
  const requiresUser = to.meta.requiresUser
  const requiresGuest = to.meta.requiresGuest

  // 1. Redirect already authenticated users from other guest-only pages
  if (requiresGuest && isAuthenticated()) {
    console.log('Redirecting authenticated user from guest-only page')
    return next(isAdmin() ? '/admin' : '/dashboard')
  }

  // 2. Redirect unauthenticated users from protected pages to login
  if (requiresAuth && !isAuthenticated()) {
    console.log('Redirecting unauthenticated user to login')
    return next('/login')
  }

  // 3. Redirect authenticated users to their correct dashboards based on role
  if (isAuthenticated()) {
    if (requiresAdmin && !isAdmin()) {
      console.log('Redirecting non-admin from admin page')
      return next('/dashboard')
    }
    if (requiresUser && isAdmin()) {
      console.log('Redirecting admin from user page')
      return next('/admin')
    }
  }

  // 4. Proceed to the requested route
  console.log('Proceeding to requested route')
  next()
})

export default router