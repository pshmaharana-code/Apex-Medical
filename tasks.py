from celery_worker import celery_app
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# -- The core email function --- 
def send_email(to_address, subject, message, content="html"):
    #Create the envolope
    msg = MIMEMultipart()
    msg['To'] = to_address
    msg['From'] = 'billing@apexhospital.com'
    msg['Subject'] = subject

    #put the letter inside the envelop
    if content == 'html':
        msg.attach(MIMEText(message, 'html'))
    else:
        msg.attach(MIMEText(message, 'plain'))

    # Hand it to the post office(MailHog)
    try:
        # Mailhog listen on localhost:1025
        s = smtplib.SMTP(host='localhost', port=1025)
        s.send_message(msg)
        s.quit()

    except Exception as e:
        print(f"Failed to send email: {e}")

# ---- The background task---
# This decorator transforms a normal function into a background task
@celery_app.task
def send_payment_receipt(user_email, patient_name):
    print(f"Starting email task for {patient_name}...")

    subject = "Appointment Confirmed - Apex Hospital Receipt"
    
    # A beautiful HTML receipt for the patient
    html_message = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #eee; border-radius: 10px;">
        <h2 style="color: #0f766e;">Payment Successful!</h2>
        <p>Hi <strong>{patient_name}</strong>,</p>
        <p>Your appointment has been successfully booked and your payment has cleared.</p>
        <div style="background-color: #f8fafc; padding: 15px; border-radius: 8px; margin: 20px 0;">
            <p style="margin: 0;"><strong>Status:</strong> <span style="color: #10b981;">Confirmed</span></p>
        </div>
        <p>Thank you for trusting Apex Hospital.</p>
    </div>
    """
    
    # Send it using our core function
    send_email(to_address=user_email, subject=subject, message=html_message, content="html")
    return f"Receipt successfully sent to {user_email}"



from celery import shared_task
from models import Appointment, User
from extension import db
from datetime import datetime 
import pytz

@shared_task(name='tasks.send_daily_reminders')
def send_daily_reminders():
    # 1. Force Python to calculate "today" using Indian Standard Time
    ist_timezone = pytz.timezone('Asia/Kolkata')
    today = datetime.now(ist_timezone).date()

    # 2. Find all active appointments for today
    todays_appointments = Appointment.query.filter_by(date=today, status='Booked').all()

    if not todays_appointments:
        print(f"[{today}] No appointments scheduled for today. Skipping reminders.")
        return "No reminders sent."
    
    # 3. Loop through and SEND real emails via MailHog
    count = 0
    for appt in todays_appointments:
        patient_user = User.query.get(appt.patient.user_id)
        doctor_name = appt.doctor.name
        appt_time = appt.time.strftime('%I:%M %p')

        if patient_user and patient_user.email:
            subject = "Reminder: Your Appointment Today"
            
            html_message = f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #eee; border-radius: 10px;">
                <h2 style="color: #0f766e;">Appointment Reminder</h2>
                <p>Hi <strong>{appt.patient.name}</strong>,</p>
                <p>This is an automated reminder for your consultation today.</p>
                <div style="background-color: #f8fafc; padding: 15px; border-radius: 8px; margin: 20px 0;">
                    <p style="margin: 5px 0;"><strong>Doctor:</strong> Dr. {doctor_name}</p>
                    <p style="margin: 5px 0;"><strong>Time:</strong> {appt_time}</p>
                </div>
                <p>Please arrive 10 minutes early. Thank you for choosing Apex Hospital.</p>
            </div>
            """
            
            from tasks import send_email # Ensure your helper is imported
            send_email(to_address=patient_user.email, subject=subject, message=html_message, content="html")
            count += 1

    return f"Successfully sent {count} daily reminders via MailHog."