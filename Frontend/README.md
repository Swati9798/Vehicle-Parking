# Vehicle Parking Frontend

A modern Vue.js frontend application for the Vehicle Parking Management System.

## 🚀 Features

- **Modern Design**: Glass morphism effects with gradient backgrounds
- **Responsive Layout**: Works perfectly on desktop, tablet, and mobile devices
- **User Dashboard**: View parking lots, make reservations, manage bookings
- **Admin Dashboard**: Manage parking lots, view statistics, user management
- **Real-time Updates**: Live status updates for parking availability
- **Secure Authentication**: JWT-based authentication with role-based access
- **Toast Notifications**: User-friendly success/error messages

## 🛠️ Tech Stack

- **Vue.js 3** - Progressive JavaScript framework
- **Vue Router 4** - Official router for Vue.js
- **Bootstrap 5** - CSS framework for responsive design
- **Bootstrap Icons** - Icon library
- **Axios** - HTTP client for API calls
- **Vite** - Fast build tool and development server

## 📦 Installation

1. **Install Dependencies**
   ```bash
   cd frontend
   npm install
   ```

2. **Start Development Server**
   ```bash
   npm run dev
   ```

3. **Access the Application**
   Open your browser and navigate to `http://localhost:5173`

## 🏗️ Project Structure

```
frontend/
├── public/                 # Static assets
├── src/
│   ├── assets/            # CSS, images, and other assets
│   │   └── styles.css     # Global styles and modern CSS
│   ├── components/        # Reusable Vue components
│   │   └── LoadingSpinner.vue
│   ├── services/          # API services and utilities
│   │   ├── api.js         # Axios configuration
│   │   ├── auth.js        # Authentication service
│   │   └── parking.js     # Parking and admin services
│   ├── views/             # Page components
│   │   ├── Home.vue       # Landing page
│   │   ├── Login.vue      # User login
│   │   ├── Register.vue   # User registration
│   │   ├── UserDashboard.vue    # User dashboard
│   │   └── AdminDashboard.vue   # Admin dashboard
│   ├── router/            # Vue Router configuration
│   │   └── index.js       # Route definitions and guards
│   ├── App.vue            # Root component
│   └── main.js            # Application entry point
├── index.html             # HTML template
├── package.json           # Dependencies and scripts
└── vite.config.js         # Vite configuration
```

## 🔐 Authentication & Authorization

### User Roles
- **User**: Can view parking lots, make reservations, manage their bookings
- **Admin**: Full access to manage parking lots, view all reservations and users

### Demo Credentials
- **Admin**: `admin` / `admin123`
- **User**: Register a new account or use any created user account

## 🎨 Design Features

### Modern UI Elements
- Glass morphism effects with backdrop blur
- Gradient backgrounds and buttons
- Smooth animations and transitions
- Responsive design for all screen sizes
- Custom scrollbars and form controls

### Color Scheme
- Primary Gradient: `#667eea` to `#764ba2`
- Success: `#198754`
- Warning: `#ffc107`
- Danger: `#dc3545`
- Info: `#0dcaf0`

## 🔧 API Integration

The frontend connects to the Flask backend API running on `http://localhost:5000/api`

### Key API Endpoints Used
- `POST /auth/login` - User authentication
- `POST /auth/register` - User registration
- `GET /parking-lots` - Get parking lots
- `POST /reservations` - Create reservations
- `PUT /reservations/{id}/release` - Release parking spots
- `GET /admin/dashboard` - Admin statistics (Admin only)
- `POST /admin/parking-lots` - Create parking lots (Admin only)

## 📱 Responsive Breakpoints

- **Mobile**: `< 576px`
- **Tablet**: `576px - 768px`
- **Desktop**: `768px - 992px`
- **Large Desktop**: `> 992px`

## 🚀 Build for Production

```bash
npm run build
```

The built files will be in the `dist/` directory, ready for deployment.

## 🔄 Development Workflow

1. **Start Backend**: Ensure the Flask backend is running on port 5000
2. **Start Frontend**: Run `npm run dev` to start the Vite development server
3. **Access Application**: Open `http://localhost:5173` in your browser

## 🎯 Key Features by Role

### Regular Users
- ✅ View available parking lots with real-time availability
- ✅ Book parking spots with vehicle information
- ✅ View current active reservations
- ✅ Release parking spots when leaving
- ✅ View reservation history with costs and duration
- ✅ Responsive mobile-friendly interface

### Admin Users
- ✅ Complete dashboard with system statistics
- ✅ Create, edit, and delete parking lots
- ✅ View all users and their information
- ✅ Monitor all reservations across the system
- ✅ Real-time updates on parking availability
- ✅ Tabbed interface for easy navigation

## 🛡️ Security Features

- JWT token-based authentication
- Automatic token refresh handling
- Route guards for protected pages
- Role-based access control
- Secure API communication
- Input validation and sanitization

## 🎨 Accessibility

- Semantic HTML structure
- ARIA labels and roles
- Keyboard navigation support
- High contrast color combinations
- Screen reader friendly
- Mobile touch targets (44px minimum)

## 🐛 Error Handling

- Global error interceptors
- User-friendly error messages
- Toast notifications for feedback
- Graceful fallbacks for failed requests
- Loading states for better UX

This frontend provides a complete, modern, and user-friendly interface for the Vehicle Parking Management System!