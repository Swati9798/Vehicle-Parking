import os
from datetime import timedelta

class Config:
    """Base configuration class"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-change-in-production'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT Configuration
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-string'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # Redis Configuration (for production)
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'
    
    # ================= CELERY CONFIGURATION (NEW) =================
    # Celery Configuration
    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL') or 'redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND') or 'redis://localhost:6379/1'
    CELERY_TASK_SERIALIZER = 'json'
    CELERY_ACCEPT_CONTENT = ['json']
    CELERY_RESULT_SERIALIZER = 'json'
    CELERY_TIMEZONE = 'UTC'
    CELERY_ENABLE_UTC = True
    CELERY_TASK_TRACK_STARTED = True
    CELERY_RESULT_EXPIRES = 3600  # Results expire after 1 hour
    
    # Celery Beat Schedule (for periodic tasks)
    CELERY_BEAT_SCHEDULE = {
        'daily-reminders': {
            'task': 'application.tasks.send_daily_reminders',
            'schedule': 60.0 * 60.0 * 18.0,  # Every day at 6 PM (18:00)
        },
        'monthly-reports': {
            'task': 'application.tasks.send_monthly_reports',
            'schedule': 60.0 * 60.0 * 24.0 * 30.0,  # Every 30 days
        },
    }
    # ===============================================================
    
    # Mail Configuration
    # IIT Madras SMTP Configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'  # IIT might use Gmail
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or 'mswati9472@gmail.com'
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or 'wnreuqhqocacxnbf'
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER') or 'mswati9472@gmail.com'
    
    # Option 2: For development testing (uncomment to use MailHog)
    # MAIL_SERVER = 'localhost'
    # MAIL_PORT = 1025
    # MAIL_USE_TLS = False
    # MAIL_USE_SSL = False
    # MAIL_USERNAME = None
    # MAIL_PASSWORD = None
    # MAIL_DEFAULT_SENDER = 'noreply@parkingapp.com'

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///parking_app.db'

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///parking_app.db'

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}