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
    rows = sheet.get_all_records()
    for index, row in enumerate(rows):
        if row['Email'].strip().lower() == email.strip().lower():
            return row, index + 2  # +2 to match Google Sheets' 1-based indexing
    return None, None

