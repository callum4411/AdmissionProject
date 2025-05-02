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

def upload_file_to_drive(filepath, student_name, doc_label):
    # Get student folder (create if missing)
    folder_id = get_or_create_student_folder(student_name)

    # Filename: Passport.pdf, etc.
    filename = f"{doc_label}{os.path.splitext(filepath)[1]}"
    file_metadata = {
        'name': filename,
        'parents': [folder_id]
    }

    mimetype = mimetypes.guess_type(filepath)[0]
    media = MediaFileUpload(filepath, mimetype=mimetype)

    file = drive_service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id, webViewLink'
    ).execute()

    return file.get('webViewLink')


def get_or_create_student_folder(student_name):
    query = f"'{DRIVE_FOLDER_ID}' in parents and name = '{student_name}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    results = drive_service.files().list(q=query, fields="files(id, name)").execute()
    folders = results.get('files', [])

    if folders:
        return folders[0]['id']

    # Create the folder if it doesn't exist
    folder_metadata = {
        'name': student_name,
        'mimeType': 'application/vnd.google-apps.folder',
        'parents': [DRIVE_FOLDER_ID]
    }

    folder = drive_service.files().create(body=folder_metadata, fields='id').execute()
    return folder.get('id')
