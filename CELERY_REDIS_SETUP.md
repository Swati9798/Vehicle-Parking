# Vehicle Parking System - Backend Jobs Setup Guide

## Overview
This guide helps you set up Celery (background tasks) and Redis (caching/message broker) for the Vehicle Parking System.

## What You Need

### 1. Redis Server
Redis is used as:
- **Message Broker**: Sends tasks to Celery workers
- **Result Backend**: Stores task results
- **Cache Store**: Improves performance by caching data

### 2. Celery Workers
Celery handles:
- **Daily Reminders**: Email users who haven't parked recently
- **Monthly Reports**: Send parking usage statistics
- **CSV Export**: Generate and email parking history files
- **Cleanup Tasks**: Remove expired reservations and old files

## Setup Instructions

### Step 1: Install Python Dependencies
```bash
cd backend
# Activate your virtual environment
menv\Scripts\activate  # Windows

# Install dependencies (Celery and Redis client)
pip install -r requirements.txt
```

### Step 2: Install Redis Server

#### Windows (Recommended):
1. **Using Chocolatey** (easiest):
   ```powershell
   # Install Chocolatey if you don't have it
   Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
   
   # Install Redis
   choco install redis-64
   ```

2. **Using Windows Subsystem for Linux (WSL)**:
   ```bash
   # In WSL terminal
   sudo apt update
   sudo apt install redis-server
   sudo service redis-server start
   ```

3. **Using Docker** (if you prefer):
   ```bash
   docker run -d --name redis -p 6379:6379 redis:latest
   ```

#### Verify Redis Installation:
```bash
# Test Redis connection
redis-cli ping
# Should return: PONG
```

### Step 3: Start the Application

#### Terminal 1 - Start Flask App:
```bash
cd backend
menv\Scripts\activate
python app.py
```

#### Terminal 2 - Start Celery Worker:
```bash
cd backend
menv\Scripts\activate
celery -A celery_worker.celery worker --loglevel=info
```

#### Terminal 3 - Start Celery Beat (Optional - for scheduled tasks):
```bash
cd backend
menv\Scripts\activate
celery -A celery_worker.celery beat --loglevel=info
```

## Testing Background Tasks

### 1. Test CSV Export
```bash
# Login to your app and make this API call:
POST http://localhost:5000/api/export/csv
Headers: Authorization: Bearer <your-jwt-token>

# Should return task ID and status
```

### 2. Test Admin Tasks (Admin login required)
```bash
# Trigger daily reminders
POST http://localhost:5000/api/admin/tasks/trigger-reminders
Headers: Authorization: Bearer <admin-jwt-token>

# Trigger monthly reports
POST http://localhost:5000/api/admin/tasks/trigger-reports
Headers: Authorization: Bearer <admin-jwt-token>

# Check task status
GET http://localhost:5000/api/admin/tasks/status/<task-id>
Headers: Authorization: Bearer <admin-jwt-token>
```

## Scheduled Tasks

When Celery Beat is running, these tasks run automatically:

| Task | Schedule | Description |
|------|----------|-------------|
| Daily Reminders | 6:00 PM daily | Email inactive users |
| Monthly Reports | 1st of month, 9:00 AM | Send usage statistics |
| Cleanup Expired | 2:00 AM daily | Free up expired parking spots |

## Monitoring

### Celery Flower (Optional Web UI):
```bash
# Install Flower
pip install flower

# Start Flower dashboard
celery -A celery_worker.celery flower
# Visit: http://localhost:5555
```

### Redis CLI Monitoring:
```bash
# Monitor Redis commands
redis-cli monitor

# Check Redis info
redis-cli info
```

## Common Issues

### Issue: Redis Connection Error
**Error**: `ConnectionError: Error 10061 connecting to localhost:6379`
**Solution**: Start Redis server
```bash
# Windows with Chocolatey
redis-server

# WSL
sudo service redis-server start

# Docker
docker start redis
```

### Issue: Celery Import Errors
**Error**: `ImportError: No module named 'celery'`
**Solution**: Ensure virtual environment is activated and dependencies installed
```bash
menv\Scripts\activate
pip install -r requirements.txt
```

### Issue: Tasks Not Running
**Error**: Tasks submitted but not executing
**Solution**: Check Celery worker is running and Redis is accessible

## Environment Variables (Optional)

Create a `.env` file in the backend folder:
```env
# Redis Configuration
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Email Configuration (for notifications)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=your-email@gmail.com
```

## Production Deployment

For production, consider:

1. **Redis Persistence**: Configure Redis to persist data
2. **Process Management**: Use supervisord or systemd for Celery workers
3. **Load Balancing**: Multiple Celery workers across servers
4. **Monitoring**: Use Flower, Sentry, or similar tools
5. **Security**: Redis authentication and SSL connections

## File Structure

After setup, your backend should look like:
```
backend/
├── app.py                 # Main Flask app
├── celery_worker.py       # Celery worker entry point
├── celery_config.py       # Celery configuration
├── requirements.txt       # Dependencies (updated)
├── application/
│   ├── celery_init.py     # Celery initialization
│   ├── tasks.py           # Background task definitions
│   ├── config.py          # App configuration (updated)
│   ├── routes.py          # API routes (updated with task endpoints)
│   └── ...
└── static/
    └── exports/           # CSV export directory
```

## Next Steps

1. Install Redis server
2. Start all components (Flask, Celery Worker, Celery Beat)
3. Test the new API endpoints
4. Monitor logs for any issues
5. Implement Redis caching for better performance