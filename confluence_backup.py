import requests
import time
import re
import json
import logging

JSON_DATA = b'{"cbAttachments": "true", "exportToCloud": "true"}'  # Constants (DO NOT CHANGE)


def conf_backup(account, username, token, json_, folder):

    # global variables
    global backup_response
    global file_name

    # Create the full base url for the JIRA instance using the account name.
    url = 'https://' + account + '.atlassian.net/wiki'

    # Open new session for cookie persistence and auth.
    session = requests.Session()
    session.auth = (username, token)
    session.headers.update({"Accept": "application/json", "Content-Type": "application/json"})

    # Start backup
    backup_start = session.post(url + '/rest/obm/1.0/runbackup', data=json_)

    # Catch error response from backup start and exit if error found.
    try:
        backup_response = int(re.search('(?<=<Response \[)(.*?)(?=\])', str(backup_start)).group(1))
    except AttributeError:
        print(backup_start.text)
        logging.error('CONFLUENCE: ' + backup_start.text)
        return

    # Check backup startup response is 200 if not print error and exit.
    if backup_response != 200:
        print(backup_start.text)
        logging.error('CONFLUENCE: ' + backup_start.text)
        return
    else:
        print('Backup starting...')

    progress_req = session.get(url + '/rest/obm/1.0/getprogress')

    # Check for filename match in response
    file_name = str(re.search('(?<=fileName\":\")(.*?)(?=\")', progress_req.text))

    # If no file name match in JSON response keep outputting progress every 10 seconds
    while file_name == 'None':

        progress_req = session.get(url + '/rest/obm/1.0/getprogress')
        # Regex to extract elements of JSON progress response.
        file_name = str(re.search('(?<=fileName\":\")(.*?)(?=\")', progress_req.text))
        estimated_percentage = str(re.search('(?<=Estimated progress: )(.*?)(?=\")', progress_req.text))
        error = 'error'
        # While there is an estimated percentage this will be output.
        if estimated_percentage != 'None':
            # Regex for current status.
            current_status = str(
                re.search('(?<=currentStatus\":\")(.*?)(?=\")', progress_req.text).group(1))
            # Regex for percentage progress value
            estimated_percentage_value = str(
                re.search('(?<=Estimated progress: )(.*?)(?=\")', progress_req.text).group(1))
            print('Action: ' + current_status + ' / Overall progress: ' + estimated_percentage_value)
            time.sleep(10)
        # Once no estimated percentage in response the alternative progress is output.
        elif estimated_percentage == 'None':
            # Regex for current status.
            current_status = str(
                re.search('(?<=currentStatus\":\")(.*?)(?=\")', progress_req.text).group(1))
            # Regex for alternative percentage value.
            alt_percentage_value = str(
                re.search('(?<=alternativePercentage\":\")(.*?)(?=\")', progress_req.text).group(1))
            print('Action: '+ current_status + ' / Overall progress: ' + alt_percentage_value)
            time.sleep(10)
        # Catch any instance of the of word 'error' in the response and exit script.
        elif error.casefold() in progress_req.text:
            print(progress_req.text)
            logging.error('CONFLUENCE: ' + progress_req.text)

            return

    # Get filename from progress JSON
    file_name = str(re.search('(?<=fileName\":\")(.*?)(?=\")', progress_req.text))

    # Check filename is not None
    if file_name != 'None':
        file_name = str(re.search('(?<=fileName\":\")(.*?)(?=\")', progress_req.text).group(1))

        # print('Backup complete, downloading file to ' + folder)
        # print('Backup file can also be downloaded from ' + url + '/wiki/download/' + file_name)

        logging.info('Backup complete, downloading file to: {}'.format(folder))
        logging.info('Backup file can also be downloaded from ' + url + '/wiki/download/' + file_name)

        date = time.strftime("%d%m%Y")

        filename = account + '_conf_backup_' + date + '.zip'

        file = session.get(url + '/download/' + file_name, stream=True)

        file.raise_for_status()

        with open(folder + filename, 'wb') as handle:
            for block in file.iter_content(1024):
                handle.write(block)
        return filename


def main():
    with open('backup_data.json', 'r') as backup_data_json:
        backup_data = json.load(backup_data_json)

    site = backup_data.get('site')
    user_name = backup_data.get('user_name')
    api_token = backup_data.get('api_token')

    folder = 'confluence_backups/'

    return conf_backup(site, user_name, api_token, JSON_DATA, folder)
