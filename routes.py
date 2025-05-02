import os
import random
import smtplib
from email.message import EmailMessage
from sheets import get_student_by_email, sheet, get_all_students
from flask import render_template, request, redirect, url_for, session, flash
from app import app
from drive_upload import upload_file_to_drive
from sheets import get_student_by_email  # You’ll update the sheet here too

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

    # ✅ Fetch row from Google Sheet
    row, _ = get_student_by_email(session['user'])  # ✅ Fixes tuple unpacking issue


    if not row:
        flash("Your email was not found in the admissions sheet.", "error")
        return redirect(url_for('logout'))

    # ✅ Build document link/status dictionary
    grade_level = int(row.get('Grade', 0))

    documents = {
        'School Transfer Certificate': row.get('School Transfer Certificate'),
        'Emirates ID/Diplomatic ID': row.get('Emirates ID/Diplomatic ID'),
        'Emirates ID Declaration Letter and Undertaking Form': row.get(
            'Emirates ID Declaration Letter and Undertaking Form'),
        'Official Copy of the Final Report Card for previous year': row.get(
            'Official Copy of the Final Report Card for previous year')
    }

    # Only show transcript field for grades 10–12
    if grade_level >= 10:
        documents['Official Copy of Transcript'] = row.get('Official Copy of Transcript')

    return render_template('dashboard.html', user=session['user'], documents=documents)
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# Make sure user is logged in
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'user' not in session:
        return redirect(url_for('login'))

    # Define all documents
    fields = {
        'transfer_certificate': 'School Transfer Certificate',
        'emirates_id': 'Emirates ID/Diplomatic ID',
        'declaration_letter': 'Emirates ID Declaration Letter and Undertaking Form',
        'report_card': 'Official Copy of the Final Report Card for previous year',
        'transcript': 'Official Copy of Transcript'
    }

    # Get student data
    row, row_index = get_student_by_email(session['user'])
    if not row:
        flash("Student not found.", "error")
        return redirect(url_for('dashboard'))

    student_name = row.get('Student Name')
    grade_level = int(row.get('Grade', 0))

    # Remove transcript if under grade 10
    if grade_level < 10:
        fields.pop('transcript', None)

    if request.method == 'POST':
        upload_success = False

        for field, doc_label in fields.items():
            file = request.files.get(field)
            print(f"[DEBUG] Checking field '{field}' → file: {file.filename if file else 'None'}")

            if file and file.filename:
                save_path = os.path.join('uploads', session['user'], file.filename)
                os.makedirs(os.path.dirname(save_path), exist_ok=True)
                file.save(save_path)
                print(f"[DEBUG] Saved file to {save_path}")

                try:
                    drive_link = upload_file_to_drive(save_path, student_name, doc_label)
                    print(f"[DEBUG] Uploaded to Drive: {drive_link}")

                    col_index = list(row.keys()).index(doc_label) + 1
                    sheet.update_cell(row_index, col_index, drive_link)
                    upload_success = True

                except Exception as e:
                    print(f"[ERROR] Upload failed for {doc_label}: {e}")
                    flash(f"Failed to upload {doc_label}.", "error")

        if upload_success:
            flash("Documents uploaded successfully.", "success")
        else:
            flash("No documents were uploaded.", "error")

        return redirect(url_for('dashboard'))

    # For GET — show only missing docs
    missing_docs = {
        field: label
        for field, label in fields.items()
        if not row.get(label)
    }

    return render_template('upload.html', missing_docs=missing_docs)
