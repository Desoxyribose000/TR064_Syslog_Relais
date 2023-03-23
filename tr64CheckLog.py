import requests
from requests.auth import HTTPDigestAuth
import syslog


credentials_filename = "credentials.ini"
logs_filename = "tr064.log"

# ---------------- Implementation for Linux Service --------------------------------------------------------------------

# [Unit]
# Description = Logging service for Tr-064 Device
# After = network.target  # Assuming you want to start after network interfaces are made available
#
# [Service]
# Type = simple
# ExecStart = python < Path to File >
# User =  # User to run the script as
# Group =  # Group to run the script as
# Restart = on - failure  # Restart when there are errors
# SyslogIdentifier = TR-064 Relais Service
# RestartSec = 5
# TimeoutStartSec = infinity
#
# [Install]
# WantedBy = multi - user.target  # Make it accessible to other users


# File is intended to be executed as a service or cron job on linux repeatedly
# needs error handling if something in the connection went wrong
# needs initial setup for making HOST, PORT, UID and PASSWD available
# build cron job version und service version (terminated version, recuring loop)

# vorraussetzung installiertes syslog monitoring für client

# persistent data in /var/app_name/logs

# secret handling???? file with permissions?


# todo:
# cron job vs linux service
#   add Unit File for Linux Service


# Used for more granular Error handling acording to HTTP Response Code
class CustomError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return "Error: %s" % self.value


def get_log_from_tr64(host, port, uid, passwd):
    payload = """<?xml version="1.0"?>
    <s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/"
    s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
    <s:Body><u:GetDeviceLog xmlns:u="urn:dslforumorg:service:DeviceInfo:1"></u:GetDeviceLog>
    </s:Body>
    </s:Envelope>"""

    headers = {
        'Content-Type': 'text/xml; charset=utf-8',
        'SOAPACTION': 'urn:dslforum-org:service:DeviceInfo:1#GetDeviceLog'
    }

    locator = "/upnp/control/deviceinfo"

    url = "http://" + host + ":" + port + locator
    try:
        response = requests.request("POST", url, headers=headers, data=payload, auth=HTTPDigestAuth(uid, passwd))

        try:
            if response == "<Response [200]>":
                pass
            elif response == "<Response [401]>":
                raise CustomError("TR-064 Relais failed to authorize with TR-064 Log Origin Device")
        except CustomError:
            syslog.syslog(syslog.LOG_ERR, str(CustomError))
            raise CustomError

    except Exception:
        syslog.syslog(syslog.LOG_ERR, str(Exception))
        raise Exception

    try:
        temp, garbage = response.text.split("</NewDeviceLog>", 1)

        garbage, temp = temp.split("<NewDeviceLog>", 1)

        events = temp.split("\n")

        return events

    except Exception:
        syslog.syslog(syslog.LOG_ERR, str(Exception))
        raise Exception


def get_credentials_from_file(file):
    # get credentials needed for execution from a file
    try:
        with open(file, 'rt') as file:
            lines = [str(line.strip()) for line in file]

        return lines

    except Exception:
        syslog.syslog(syslog.LOG_ERR, "Error in reading files for TR064 logging service " + str(Exception))
        raise Exception


def get_logs_from_file(file):
    # get logs from file if file not existend return empty lines
    try:
        with open(file, 'rt') as file:
            lines = [str(line.strip()) for line in file]

    except Exception:
        syslog.syslog(syslog.LOG_INFO, "New Log File will be created for TR064 logging service")
        lines = ""

    return lines


def compare_logs(file_logs, tr64logs):
    # compares new logs from tr064 with logs saved in file
    # if new log entries exist return them, if not return none

    try:

        if file_logs:

            new_messages = list(set(file_logs - tr64logs))

        else:
            new_messages = tr64logs

        return new_messages

    except Exception:
        syslog.syslog(syslog.LOG_ERR, "Error in comparing files for TR064 logging service " + str(Exception))
        raise Exception


def log_to_syslog_and_file(new_logs, filename):
    # log all new log entries to syslog and add them afterwards to the file of logged messsages

    try:
        logfile = open(filename, "at")

        for line in new_logs:
            syslog.syslog(syslog.LOG_INFO, line)
            logfile.write(line + "\n")

        logfile.close()
        return 1

    except Exception:
        syslog.syslog(syslog.LOG_ERR, "Error in logging new messages for TR064 logging service " + str(Exception))
        raise Exception


# HOST = lines[0], PORT = lines[1], UID = lines[2], PASSWD = lines[3]
creds = get_credentials_from_file(credentials_filename)

logs_from_file = get_logs_from_file(logs_filename)

logs_from_device = get_log_from_tr64(creds[0], creds[1], creds[2], creds[3])

new_log_messages = compare_logs(logs_from_file, logs_from_device)

exit(log_to_syslog_and_file(new_log_messages, logs_filename))
