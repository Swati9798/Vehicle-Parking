from celery import Celery

def create_celery(app=None):
    """
    Create and configure a Celery instance with Redis broker.
    If a Flask app is passed, integrate it with app context.
    """
    # Use Redis instead of memory
    celery = Celery(
        app.import_name if app else "vehicle_parking",
        broker='redis://localhost:6379/0',      # Redis as message broker
        backend='redis://localhost:6379/1',     # Redis as result backend
        include=['application.tasks']           # Import tasks module
    )

    if app:
        # Update Celery config with Flask app config
        celery.conf.update(app.config)
        
        # Attach Flask app context to Celery tasks
        class ContextTask(celery.Task):
            def __call__(self, *args, **kwargs):
                with app.app_context():
                    return self.run(*args, **kwargs)
        celery.Task = ContextTask

    return celery


# 👇 Expose a global celery instance with Redis (for CLI `-A` usage)
celery = Celery(
    "vehicle_parking",
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/1',
    include=['application.tasks']
)

# Configure the global celery instance
celery.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    result_expires=3600,
)