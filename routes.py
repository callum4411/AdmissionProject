import random
import smtplib
from email.message import EmailMessage
from sheets import get_student_by_email
from flask import render_template, request, redirect, url_for, session, flash
from app import app

# 🔧 Configure your email account (use school Gmail ideally)
EMAIL_ADDRESS = 'smithcallum918@gmail.com'
EMAIL_PASSWORD = 'binpxxwtlosjhlnr'  # ← paste your app password here as one string


@app.route('/')
def home():
    return redirect(url_for('login'))
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email').strip()

        student = get_student_by_email(email)

        if student:
            code = str(random.randint(100000, 999999))
            session['pending_email'] = email
            session['verification_code'] = code

            # Send the code by email
            try:
                msg = EmailMessage()
                msg['Subject'] = 'Your ACS Admissions Login Code'
                msg['From'] = EMAIL_ADDRESS
                msg['To'] = email
                msg.set_content(f'Hello,\n\nYour ACS login verification code is: {code}\n\nThank you.')

                with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                    smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
                    smtp.send_message(msg)

                return redirect(url_for('verify'))

            except Exception as e:
                print("Email error:", e)
                flash('Error sending verification email. Please try again later.', 'error')
        else:
            flash('Email not found in the admissions system.', 'error')

    return render_template('login.html')


@app.route('/verify', methods=['GET', 'POST'])
def verify():
    if request.method == 'POST':
        code_entered = request.form.get('code')
        if code_entered == session.get('verification_code'):
            session['user'] = session.get('pending_email')
            session.pop('verification_code', None)
            session.pop('pending_email', None)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid verification code. Please try again.', 'error')

    return render_template('verify.html')
@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))

    # ✅ Get student record from Google Sheets
    student = get_student_by_email(session['user'])

    if not student:
        flash("No record found in admissions system. Please contact support.")
        return redirect(url_for('logout'))

    # ✅ Read document completion status from the sheet
    documents = {
        'Passport': str(student.get('Passport', '')).lower() == 'true',
        'Vaccine Card': str(student.get('Vaccine Card', '')).lower() == 'true',
        'Emirates ID': str(student.get('Emirates ID', '')).lower() == 'true',
        'Residence Visa': str(student.get('Residence Visa', '')).lower() == 'true'
    }

    return render_template('dashboard.html', user=session['user'], documents=documents)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))
