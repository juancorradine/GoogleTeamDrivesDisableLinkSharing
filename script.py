from __future__ import print_function
import httplib2
import os
import time
import datetime

from googleapiclient.errors import HttpError
from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

try:
    import argparse

    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/drive-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/drive'
CLIENT_SECRET_FILE = 'drive-python-quickstart.json'
APPLICATION_NAME = 'Drive API Quickstart'

teamdrives = {}
teamdrivefiles = {}
processedteamdrivefiles = {}


def get_timestamp():
    return str(datetime.datetime.now()).split('.')[0]


def get_credentials():
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   CLIENT_SECRET_FILE)

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        credentials = tools.run_flow(flow, store, flags)

    return credentials


def delete_file_permissions():
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    drive_service = discovery.build('drive', 'v3', http=http)

    for key, value in teamdrivefiles.items():
        if value == '':
            continue

        for permission in value:
            should_restart = True
            while should_restart:
                try:
                    response = drive_service.permissions().delete(fileId=key,
                                                                  permissionId=permission,
                                                                  supportsTeamDrives='true').execute()
                    if response == '':
                        processedteamdrivefiles[key] = 'Cleared.'
                        should_restart = False

                except HttpError as err:
                    error_message = err.__str__()[err.__str__().find("returned \"") + 10:-2]
                    if err.resp.status == 403 and error_message == "User Rate Limit Exceeded":
                        print(get_timestamp() + " - User rate limit exceeded. Waiting for 101 seconds..")
                        time.sleep(101)
                        print(get_timestamp() + " - Restarting...")
                    elif err.resp.status == 500:
                        print(get_timestamp() + " - Error 500: " + error_message + ".")
                        print(get_timestamp() + " - Retrying in 3 seconds...")
                        time.sleep(3)
                    else:
                        processedteamdrivefiles[key] = "Error " + str(err.resp.status) + ". " + error_message


def get_file_permission_id():
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    drive_service = discovery.build('drive', 'v3', http=http)

    for key, value in teamdrivefiles.items():
        mypermissions = []
        should_restart = True
        page_token = None
        while should_restart:
            try:
                response = drive_service.permissions().list(fileId=key,
                                                            supportsTeamDrives='true',
                                                            pageToken=page_token).execute()
                for permission in response.get('permissions', []):
                    if permission.get('type') == 'domain' or permission.get('type') == 'anyone':
                        mypermissions.append(permission.get('id'))
                page_token = response.get('nextPageToken', None)
                if page_token is None:
                    should_restart = False
            except HttpError as err:
                error_message = err.__str__()[err.__str__().find("returned \"") + 10:-2]
                if err.resp.status == 403 and error_message == "User Rate Limit Exceeded":
                    print(get_timestamp() + " - User rate limit exceeded. Waiting for 101 seconds..")
                    time.sleep(101)
                    print(get_timestamp() + " - Restarting...")
                elif err.resp.status == 500:
                    print(get_timestamp() + " - Error 500: " + error_message + ".")
                    print(get_timestamp() + " - Retrying in 3 seconds...")
                    time.sleep(3)
                else:
                    raise
        teamdrivefiles[key] = mypermissions


def get_files_in_teamdrive(teamdrive_id):
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    drive_service = discovery.build('drive', 'v3', http=http)

    should_restart = True
    page_token = None
    while should_restart:
        try:
            response = drive_service.files().list(corpora='teamDrive',
                                                  q='mimeType != \'application/vnd.google-apps.folder\'',
                                                  teamDriveId=teamdrive_id,
                                                  includeTeamDriveItems='true',
                                                  supportsTeamDrives='true',
                                                  pageToken=page_token).execute()
            for file in response.get('files', []):
                teamdrivefiles[file.get('id')] = ''
            page_token = response.get('nextPageToken', None)
            if page_token is None:
                should_restart = False
        except HttpError as err:
            error_message = err.__str__()[err.__str__().find("returned \"") + 10:-2]
            if err.resp.status == 403 and error_message == "User Rate Limit Exceeded":
                print(get_timestamp() + " - User rate limit exceeded. Waiting for 101 seconds..")
                time.sleep(101)
                print(get_timestamp() + " - Restarting...")
            elif err.resp.status == 500:
                print(get_timestamp() + " - Error 500: " + error_message + ".")
                print(get_timestamp() + " - Retrying in 3 seconds...")
                time.sleep(3)
            else:
                raise


def get_teamdrives():
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    drive_service = discovery.build('drive', 'v3', http=http)

    should_restart = True
    page_token = None
    while should_restart:
        try:
            response = drive_service.teamdrives().list(useDomainAdminAccess='true',
                                                       pageToken=page_token).execute()

            for a in response.get('teamDrives', []):
                teamdrives[a.get('id')] = a.get('name')
            page_token = response.get('nextPageToken', None)
            if page_token is None:
                should_restart = False
        except HttpError as err:
            error_message = err.__str__()[err.__str__().find("returned \"") + 10:-2]
            if err.resp.status == 403 and error_message == "User Rate Limit Exceeded":
                print(get_timestamp() + " - User rate limit exceeded. Waiting for 101 seconds..")
                time.sleep(101)
                print(get_timestamp() + " - Restarting...")
            elif err.resp.status == 500:
                print(get_timestamp() + " - Error 500: " + error_message + ".")
                print(get_timestamp() + " - Retrying in 3 seconds...")
                time.sleep(3)
            else:
                raise


def print_teamdrives():
    print("\n" + get_timestamp() + " - List of Team Drives to process: ")
    for key, value in teamdrives.items():
        print("  " + value + " (" + key + ")")


def start():
    errors_reported = False
    print(get_timestamp() + " - Starting...")
    print(get_timestamp() + " - Getting list of Team Drives...")
    get_teamdrives()
    print_teamdrives()
    for key, value in teamdrives.items():
        print("\n***********")
        print("Starting with Teamdrive " + value + " (" + key + ").")
        print(get_timestamp() + " - Getting Team Drive files list...")
        get_files_in_teamdrive(key)
        print(get_timestamp() + " - Getting Team Drive files permissions ids...")
        get_file_permission_id()
        print(get_timestamp() + " - Clearing file permissions...")
        delete_file_permissions()
        print(get_timestamp() + " - Done!")
        if errors_reported:
            print(get_timestamp() + " - Errors reported:")
            for key2, value2 in processedteamdrivefiles:
                if 'Error' in value2:
                    print("  File id: " + key2 + ". " + value2)
        teamdrivefiles.clear()
        processedteamdrivefiles.clear()

        errors_reported = False


if __name__ == '__main__':
    start()
