from celery_worker import celery_app
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

from celery import shared_task
from models import Appointment, User
from extension import db
from datetime import datetime 
import pytz

import csv
import io
from datetime import datetime, timedelta
from sqlalchemy import extract

# -- The core email function --- 
def send_email(to_address, subject, message, content="html", attachment_data=None, attachment_filename=None):
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

    # ==========================================
    # NEW: THE ATTACHMENT LOGIC
    # ==========================================
    if attachment_data and attachment_filename:
        # 1. Create a raw data packet
        part = MIMEBase('application', 'octet-stream')
        
        # 2. Convert our Python string into raw bytes and pack it
        part.set_payload(attachment_data.encode('utf-8'))
        
        # 3. Encode it in Base64 (Standard internet email format)
        encoders.encode_base64(part)
        
        # 4. Add the header so the email client knows it's a downloadable file
        part.add_header(
            'Content-Disposition',
            f'attachment; filename="{attachment_filename}"'
        )
        
        # 5. Tape the packet to the envelope
        msg.attach(part)

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

@shared_task(name='tasks.generate_monthly_report')
def generate_monthly_report():
    # ==========================================
    # 1. TIME TRAVEL (Safely calculating "Last Month")
    # ==========================================
    today = datetime.now()
    first_day_of_this_month = today.replace(day=1)
    last_day_of_last_month = first_day_of_this_month - timedelta(days=1)

    target_month = last_day_of_last_month.month
    target_year = last_day_of_last_month.year
    month_name = last_day_of_last_month.strftime('%B')

    # ==========================================
    # 2. DATABASE AGGREGATION
    # ==========================================

    completed_appts = Appointment.query.filter(
        extract('month', Appointment.date) == target_month,
        extract('year', Appointment.date) == target_year,
        Appointment.status == 'Completed'
    ).all()

    total_completed = len(completed_appts)
    total_revenue = sum([appt.doctor.consultation_fee for appt in completed_appts if appt.doctor])

    # ==========================================
    # 3. IN-MEMORY CSV GENERATION
    # ==========================================
    csv_buffer = io.StringIO()
    csv_writer = csv.writer(csv_buffer)

    # Write Headers and Summary
    csv_writer.writerow(['Hospital Performance Report', f'{month_name} {target_year}'])
    csv_writer.writerow([]) 
    csv_writer.writerow(['Total Appointments Completed', total_completed])
    csv_writer.writerow(['Total Estimated Revenue (INR)', total_revenue])
    csv_writer.writerow([])

    # Write the Columns
    csv_writer.writerow(['Date', 'Patient', 'Doctor', 'Department', 'Consultation Fee'])

    # Write the Rows
    for appt in completed_appts:
        csv_writer.writerow([
            appt.date.strftime('%Y-%m-%d'),
            appt.patient.name,
            appt.doctor.name,
            appt.doctor.department.name if appt.doctor.department else 'N/A',
            appt.doctor.consultation_fee
        ])

    # Extract the raw string data from the buffer
    csv_data = csv_buffer.getvalue()
    csv_buffer.close()

    # ==========================================
    # 4. SEND THE EMAIL TO THE ADMIN
    # ==========================================
    # Find the administrator in the database
    admin_user = User.query.filter_by(role='admin').first()
    
    if admin_user and admin_user.email:
        subject = f"Monthly Hospital Report: {month_name} {target_year}"
        body = f"""
        <div style="font-family: Arial; padding: 20px;">
            <h2>Monthly Performance Report</h2>
            <p>Please find the automated hospital performance report for {month_name} attached to this email.</p>
            <p><strong>Total Consultations:</strong> {total_completed}</p>
            <p><strong>Revenue Generated:</strong> ₹{total_revenue}</p>
        </div>
        """
        
        # Fire our upgraded email engine!
        send_email(
            to_address=admin_user.email,
            subject=subject,
            message=body,
            content="html",
            attachment_data=csv_data,
            attachment_filename=f"Apex_Hospital_Report_{month_name}_{target_year}.csv"
        )
    return f"Report generated and emailed to admin."