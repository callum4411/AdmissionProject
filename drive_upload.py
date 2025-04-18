import os
import mimetypes
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.service_account import Credentials

# Setup scopes for Drive
SCOPES = ['https://www.googleapis.com/auth/drive']

# Load credentials
creds = Credentials.from_service_account_file(
    'service_account.json', scopes=SCOPES)

# Connect to Drive API
drive_service = build('drive', 'v3', credentials=creds)

# Replace with your actual folder ID
DRIVE_FOLDER_ID = '16AYRgCEP3XT8xm3XAQovdDOGogsiT7_Q'

def upload_file_to_drive(filepath, user_email, doc_label):
    # Create new filename: e.g., smithcallum918@gmail.com - Passport.pdf
    filename = f"{user_email} - {doc_label}{os.path.splitext(filepath)[1]}"

    # Define file metadata
    file_metadata = {
        'name': filename,
        'parents': [DRIVE_FOLDER_ID]
    }

    mimetype = mimetypes.guess_type(filepath)[0]
    media = MediaFileUpload(filepath, mimetype=mimetype)

    # Upload to Drive
    file = drive_service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id, webViewLink'
    ).execute()

    return file.get('webViewLink')  # Return shareable link
