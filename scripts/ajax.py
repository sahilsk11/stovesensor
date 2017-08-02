#!/usr/bin/python

print "Content-type: application/json\n\n"

import cgi
import json
import datetime
import current
import shelve
import requests

shelf = shelve.open("uid.shelve")
code = shelf["uid"]

def set_code(uid, f):
    f["uid"] = uid

form = cgi.FieldStorage()
command = form.getfirst("command", "pageload")

if (command == "pageload"):
    temperature = current.get_value("temperatures", "temperature", 1)
    status = current.get_value("calculated", "status", 1)
    if (status == "ON"):
        on_time = current.get_value("calculated", "time", 1)
        on_time = on_time.strftime("%I:%M %p")
    else:
        on_time = "none"
    time = current.get_value("temperatures", "time", 1)
    time = time.strftime("%I:%M %p on %m/%d/%y")
    d = {"temperature":temperature, "status": status, "on_time":on_time, "update_time":time, "code":code}
    j = json.dumps(d)
    print j
    
if (command == "getchart"):
    html_text = chart.print_html()
    d = {"html":html_text}
    json.dumps(d)
    print j

if (command == "initial_setup"):
    print "setting up"
    headers = {"command":"newdevice"}
    response = requests.get("https://www.iotspace.tech/stovesensor/scripts/data_storage.py", data=headers)
    numbers = []
    uid = response["code"]
    set_code(uid, shelf)
    wifi_name = ""
    wifi_password = ""
    print "success"
    
shelf.close()