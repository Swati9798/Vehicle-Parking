"""
Basic Celery Configuration for Development
"""
from celery import Celery

# Basic Celery configuration using memory broker (no Redis needed for dev)
def make_celery():
    celery = Celery(
        'parking_app',
        broker='memory://',
        backend='cache+memory://'
    )
    
    # Basic configuration
    celery.conf.update(
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json',
        timezone='UTC',
        enable_utc=True,
    )
    
    return celery

# Create Celery instance
celery = make_celery()