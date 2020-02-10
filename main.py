import pickle
import os.path
import time
import logging

import confluence_backup
import jira_backup
import upload_to_cloud

__author__ = 'Mykhailo Klimchuk'

SEC_IN_DAY = 86400
logging.basicConfig(filename="log.log", level=logging.INFO)
logging.info('START')


def run():
    """
        Jira allows you to backup once every 48 hours
        Confluence allows you to backup once every 24 hours
    :return:
    """
    current_time_stamp = int(time.time())
    logging.info('START BACKUP!')
    logging.info('DAY: {}'.format(time.strftime("%d.%m.%Y")))

    if os.path.exists('timestamp_backups.pickle'):
        with open('timestamp_backups.pickle', 'rb') as file:
            timestamp_backups = pickle.load(file)
    else:
        timestamp_backups = {
            'confluence_backup': 0,
            'jira_backup': 0,
        }

    if current_time_stamp - timestamp_backups.get('confluence_backup') <= SEC_IN_DAY or \
            timestamp_backups.get('confluence_backup') == 0:
        confluence_backup_file_name = confluence_backup.main()

        if confluence_backup_file_name is not None:
            folder = 'confluence_backups'

            file_confluence_backup = upload_to_cloud.main(folder, confluence_backup_file_name, 'Confluence')
            timestamp_backups['confluence_backup'] = current_time_stamp
            logging.info('Upload confluence_backup id={} on google drive'.format(file_confluence_backup.get('id')))

    if current_time_stamp - timestamp_backups.get('jira_backup') <= 2 * SEC_IN_DAY or \
            timestamp_backups.get('jira_backup') == 0:
        jira_backup_file_name = jira_backup.main()
        if jira_backup_file_name is not None:
            folder = 'jira_backups'
            file_jira_backup = upload_to_cloud.main(folder, jira_backup_file_name, 'Jira')
            timestamp_backups['jira_backup'] = current_time_stamp
            logging.info('Upload jira_backup id={} on google drive'.format(file_jira_backup.get('id')))

    with open('timestamp_backups.pickle', 'wb') as file:
        pickle.dump(timestamp_backups, file)

    logging.info('FINISH BACKUP!')
    time.sleep(SEC_IN_DAY)


if __name__ == '__main__':
    run()
