#!/usr/bin/python

print "Content-type: application/json\n\n"

import cgi
import json
import datetime
import current
import shelve
import requests

shelf = shelve.open("uid.shelve")
if (not "uid" in shelf):
    shelf["uid"] = None
code = shelf["uid"]

def set_code(uid, f):
    print(uid)
    f["uid"] = uid

form = cgi.FieldStorage()
command = form.getfirst("command", "pageload")
code = form.getfirst("code", "")

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
    print(response.text())
    numbers = []
    uid = response["uid"]
    set_code(uid, shelf)
    wifi_name = ""
    wifi_password = ""
    print "success"
    
if (command == "code_set"):
    code_set = (code != None and code != 2468)
    d = {"code_set":code_set, "code":code}
    j = json.dumps(d)
    print j
    
if (command == "set_code"):
    shelf["uid"] = int(code)
    
shelf.close()