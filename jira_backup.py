import requests
import time
import re
import json
import logging

JSON_DATA = b'{"cbAttachments": "true", "exportToCloud": "true"}'  # Constants (DO NOT CHANGE)


def jira_backup(account, username, token, json_, folder):

    # Create the full base url for the JIRA instance using the account name.
    url = 'https://' + account + '.atlassian.net'

    # Open new session for cookie persistence and auth.
    session = requests.Session()
    session.auth = (username, token)
    session.headers.update({"Accept": "application/json", "Content-Type": "application/json"})

    # Start backup
    backup_req = session.post(url + '/rest/backup/1/export/runbackup', data=json_)

    # Catch error response from backup start and exit if error found.
    if 'error' in backup_req.text:
        print(backup_req.text)
        logging.error(backup_req.text)
        return

    # Get task ID of backup.
    task_req = session.get(url + '/rest/backup/1/export/lastTaskId')
    task_id = task_req.text

    # set starting task progress values outside of while loop and if statements.
    task_progress = 0
    last_progress = -1
    global progress_req

    # Get progress and print update until complete
    while task_progress < 100:

        progress_req = session.get(url + '/rest/backup/1/export/getProgress?taskId=' + task_id)

        # Chop just progress update from json response
        try:
            task_progress = int(re.search('(?<=progress":)(.*?)(?=,)', progress_req.text).group(1))
        except AttributeError:
            print(progress_req.text)
            logging.error(progress_req.text)

            return

        if (last_progress != task_progress) and 'error' not in progress_req.text:
            print(task_progress)
            last_progress = task_progress
        elif 'error' in progress_req.text:
            print(progress_req.text)
            logging.error(progress_req.text)

            return

        if task_progress < 100:
            time.sleep(10)

    if task_progress == 100:

        download = re.search('(?<=result":")(.*?)(?=\",)', progress_req.text).group(1)

        # print('Backup complete, downloading files.')
        # print('Backup file can also be downloaded from ' + url + '/plugins/servlet/' + download)

        logging.info('Backup complete, downloading file to: {}'.format(folder))
        logging.info('Backup file can also be downloaded from ' + url + '/plugins/servlet/' + download)

        date = time.strftime("%d%m%Y")

        filename = account + '_jira_backup_' + date + '.zip'

        file = session.get(url + '/plugins/servlet/' + download, stream=True)

        file.raise_for_status()

        with open(folder + filename, 'wb') as handle:
            for block in file.iter_content(1024):
                handle.write(block)

        print(filename + 'downloaded to ' + folder)


def main():
    with open('backup_data.json', 'r') as backup_data_json:
        backup_data = json.load(backup_data_json)

    site = backup_data.get('site')
    user_name = backup_data.get('user_name')
    api_token = backup_data.get('api_token')
    folder = 'jira_backups/'

    jira_backup(site, user_name, api_token, JSON_DATA, folder)
