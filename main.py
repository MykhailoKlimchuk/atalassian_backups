import pickle
import os.path
import time
import logging
import os

import confluence_backup
import jira_backup
import upload_to_cloud

__author__ = 'Mykhailo Klimchuk'


SEC_IN_DAY = 86400
logging.basicConfig(filename=r"log.log", level=logging.INFO)
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

    confluence_backup_file_name = confluence_backup.main()
    if confluence_backup_file_name is not None:
        folder = 'confluence_backups'

        file_confluence_backup = upload_to_cloud.main(folder, confluence_backup_file_name, 'Confluence')
        logging.info('Upload confluence_backup id={} on google drive'.format(file_confluence_backup.get('id')))
    
    jira_backup_file_name = jira_backup.main()
    if jira_backup_file_name is not None:
        folder = 'jira_backups'
        file_jira_backup = upload_to_cloud.main(folder, jira_backup_file_name, 'Jira')
        logging.info('Upload jira_backup id={} on google drive'.format(file_jira_backup.get('id')))

    logging.info('FINISH BACKUP!')


if __name__ == '__main__':
    run()
