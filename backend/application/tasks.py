from celery import Celery
from flask_mail import Message
from application.mail import mail
from app import app  # Import the Flask app

# Create a simple Celery instance for tasks
celery = Celery('tasks', broker='memory://', backend='cache+memory://')

@celery.task
def send_email_task(to_email, subject, body):
    '''Send an email using Flask-Mail and Celery'''
    with app.app_context():
        msg = Message(
            subject=subject,
            recipients=[to_email],
            body=body,
            sender=app.config['MAIL_DEFAULT_SENDER']
        )
        mail.send(msg)
        print(f'Sent email to: {to_email}')
        return f'Email sent to {to_email}'
