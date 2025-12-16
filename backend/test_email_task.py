from application.tasks import send_email_task

receiver_email = input("Enter receiver email address: ")
subject = "Test Email"
body = "This is a test email sent using Celery with memory broker."

print("Testing Celery email task...")
result = send_email_task.delay(receiver_email, subject, body)
print("Task sent! Task ID:", result.id)