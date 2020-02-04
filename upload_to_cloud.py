import pickle
import os.path
import json
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaFileUpload

__author__ = 'Mykhailo Klimchuk'


SCOPES = ['https://www.googleapis.com/auth/drive']  # If modifying these scopes, delete the file token.pickle.

with open('backup_data.json', 'r') as backup_data_json:
    backup_data = json.load(backup_data_json)

BACKUPS_FOLDERS = {
    'Confluence': [backup_data.get('google_drive_confluence_folder_id')],
    'Jira': [backup_data.get('google_drive_jira_folder_id')],
}

print(BACKUPS_FOLDERS)


def main(file_name, source):
    credentials = None

    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            credentials = pickle.load(token)

    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            credentials = flow.run_local_server(port=0)

        with open('token.pickle', 'wb') as token:
            pickle.dump(credentials, token)  # Save the credentials for the next run

    service = build('drive', 'v3', credentials=credentials)

    folders = BACKUPS_FOLDERS.get(source)

    file_metadata = {'name': file_name,
                     'parents': folders}
    media = MediaFileUpload(file_name,
                            resumable=True)

    file = service.files().create(body=file_metadata,
                                  media_body=media,
                                  fields='id').execute()
    return file
