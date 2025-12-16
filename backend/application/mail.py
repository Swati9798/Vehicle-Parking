from flask_mail import Mail, Message
from flask import current_app
import os

# Initialize Flask-Mail
mail = Mail()

def send_email(to, subject, template, **kwargs):
    """Send email using Flask-Mail"""
    try:
        msg = Message(
            subject=subject,
            recipients=[to] if isinstance(to, str) else to,
            html=template,
            sender=current_app.config['MAIL_DEFAULT_SENDER']
        )
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Failed to send email: {str(e)}")
        return False

def send_daily_reminder_email(user_email, username):
    """Send daily reminder email"""
    template = f"""
    <html>
    <body>
        <h2>Daily Parking Reminder</h2>
        <p>Hello {username},</p>
        <p>This is a friendly reminder to book a parking spot if you need one today!</p>
        <p>Visit our <a href="http://localhost:5173">Parking App</a> to reserve your spot.</p>
        <br>
        <p>Best regards,<br>Parking Management Team</p>
    </body>
    </html>
    """
    return send_email(user_email, "Daily Parking Reminder", template)

def send_monthly_report_email(user_email, username, report_data):
    """Send monthly activity report email"""
    template = f"""
    <html>
    <body>
        <h2>Monthly Parking Activity Report</h2>
        <p>Hello {username},</p>
        <p>Here's your parking activity summary for this month:</p>
        
        <div style="background-color: #f5f5f5; padding: 15px; margin: 10px 0;">
            <h3>Activity Summary</h3>
            <ul>
                <li>Total Reservations: {report_data.get('total_reservations', 0)}</li>
                <li>Total Amount Spent: ${report_data.get('total_amount', 0):.2f}</li>
                <li>Most Used Location: {report_data.get('most_used_location', 'N/A')}</li>
                <li>Total Parking Hours: {report_data.get('total_hours', 0):.1f}</li>
            </ul>
        </div>
        
        <p>Thank you for using our parking service!</p>
        <br>
        <p>Best regards,<br>Parking Management Team</p>
    </body>
    </html>
    """
    return send_email(user_email, "Monthly Parking Activity Report", template)

def send_csv_export_notification(user_email, username, csv_filename):
    """Send notification when CSV export is ready"""
    template = f"""
    <html>
    <body>
        <h2>CSV Export Ready</h2>
        <p>Hello {username},</p>
        <p>Your parking history CSV export is ready for download!</p>
        <p>File: {csv_filename}</p>
        <p>You can download it from your dashboard.</p>
        <br>
        <p>Best regards,<br>Parking Management Team</p>
    </body>
    </html>
    """
    return send_email(user_email, "CSV Export Ready", template)