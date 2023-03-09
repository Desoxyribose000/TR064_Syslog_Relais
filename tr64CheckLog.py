import requests
from requests.auth import HTTPDigestAuth
import syslog

HOST = "192.168.0.115"
PORT = "49000"
UID = '#########'
PASSWD = '########'


# File is intended to be executed as a service or cron job on linux repeatedly
# needs error handling if something in the connection went wrong
# needs initial setup for making HOST, PORT, UID and PASSWD available
# build cron job version und service version (terminated version, recuring loop)

# vorraussetzung installiertes syslog monitoring für client

# secret handling???? file with permissions?


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

    url = "http://" + HOST + ":" + PORT + locator

    response = requests.request("POST", url, headers=headers, data=payload, auth=HTTPDigestAuth(UID, PASSWD))

    return response


print(get_log_from_tr64(HOST, PORT, UID, PASSWD).text)


def get_logs_from_file(file):
    # gets all earlier received logs from a file
    pass


def compare_logs(file_logs, tr64logs):
    # compares new logs from tr064 with logs saved in file
    # if new log entries exist return them, if not return none
    pass


def log_to_syslog_and_file(new_logs):
    # log all new log entries to syslog and add them afterwards to the file of logged messsages
    pass
