
This script is created for automatic backups and uploading the backups on Google Drive

backup_data.json:
1. site: name of your atlassian site
2. user_name: user with permission for backup
3. api_token: user token for use atlassian api. get here https://id.atlassian.com/manage/api-tokens
4. google_drive_confluence_folder_id: folder id on google drive for upload confluence backup
5. google_drive_jira_folder_id: folder id on google drive for upload jira backup

you need file credentials.json for use google drive api
this file you can get here: https://developers.google.com/drive/api/v3/quickstart/python (Step 1. Click on button "Enable the Drive API")

for install libs use command:
pip install -r requirements.txt

for run script use command:
python main.py

auth google account (must be account of user_name like in backup_data.json) in the default browser
browser window will open where you must to select a Google Account


Jira allows you to backup once every 48 hours!!!
Confluence allows you to backup once every 24 hours!!!

timestamp_backups.pickle contains dict with timestamps of last backups
dict has keys: confluence_backup, jira_backup

if you get error "403" or "401" delete file token.pickle and rerun script
