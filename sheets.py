import gspread
from oauth2client.service_account import ServiceAccountCredentials

# 1. Setup scopes and credentials
scope = [
    'https://spreadsheets.google.com/feeds',
    'https://www.googleapis.com/auth/drive'
]

creds = ServiceAccountCredentials.from_json_keyfile_name('service_account.json', scope)
client = gspread.authorize(creds)

# 2. Open the spreadsheet
sheet = client.open("Admissions Tracker").sheet1  # Use your sheet name

# 3. Get all students
def get_all_students():
    return sheet.get_all_records()

# 4. Get a single student's record by email
def get_student_by_email(email):
    records = get_all_students()
    for record in records:
        if record['Email'].strip().lower() == email.strip().lower():
            return record
    return None
