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
