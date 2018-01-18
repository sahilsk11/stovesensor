#!/usr/bin/python

print "Content-type: application/json\n\n"

import cgi
import json
import datetime
import current
import shelve
import requests

shelf = shelve.open("stove_data.shelve", writeback=True)
if (not "uid" in shelf):
    print("Shelf not found")
    shelf["uid"] = None
if (not "on_timer" in shelf):
    shelf["on_timer"] = 20
if (not "interval" in shelf):
    shelf["interval"] = 10
if (not "blink" in shelf):
    shelf["blink"] = True

code = shelf["uid"]

def new_code():
    headers = {"command":"newdevice"}
    response = requests.get("https://www.iotspace.tech/stovesensor/status/scripts/data_storage.py", params=headers)
    new_code = response.json()["new_code"]
    return new_code

form = cgi.FieldStorage()
command = form.getfirst("command", "pageload")
new_code = form.getfirst("code", "")
numbers = form.getfirst("phone", "")
new_timer = form.getfirst("timer", "")
new_interval = form.getfirst("interval", "")

if (code == None or code == ""):
        shelf["uid"] = new_code()
        code = shelf["uid"]

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
    
if (command == "load_setup"):
    code_set = (code != None and code != "")
    d = {"code_set":code_set, "numbers":shelf["user_info"], "code":code, "on_timer":shelf["on_timer"], "interval":shelf["interval"]}
    j = json.dumps(d)
    print j
    
if (command == "set_code"):
    if (len(new_code) == 4):
        shelf["uid"] = int(new_code)
        
if (command == "initial_setup"):
    phone_numbers = eval(numbers)
    for i in range(0, len(phone_numbers)):
        phone_numbers[i] = phone_numbers[i].replace("%2B", "+")
    shelf["user_info"] = phone_numbers
    shelf["on_timer"] = int(new_timer)
    shelf["interval"] = int(new_interval)
    d = {"success":True}
    j = json.dumps(d)
    print j
    
shelf.close()