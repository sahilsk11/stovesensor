#!/usr/bin/python

print "Content-type: application/json\n\n"

import shelve
import json
import cgi
import notification

def send_notifications(code, users):
    for user in users:
        notification.send_notification(str(user["number"]), code)

stovesensor_data = shelve.open("stove_info.shelve", writeback= True)
if (not "devices" in stovesensor_data):
        stovesensor_data["devices"] = {}

form = cgi.FieldStorage()
command = form.getfirst("command", "")
code = form.getfirst("code", "")
data = form.getfirst("data", "")

if (command == "upload"):
    json_data = eval(data)
    stovesensor_data["devices"][code] = json_data
    if (json_data["notification"]):
        send_notifications(code, json_data["numbers"])
    print {"success":True}
    print(stovesensor_data)
    
if (command == "pageload"):
    data = stovesensor_data["devices"][code]
    j = json.dumps(data)
    print j
    
if (command == "newdevice"):
    completed = False
    while (not completed):
        uid = 0
        for i in range(0, 4):
            number = random.randint(1, 9)
            uid = uid * 10 + number
        if (uid not in stovedata["devices"]):
            stovedata["devices"][uid] = {}
            completed = True
    d = {"success": True, "code":uid}
    j = json.dumps(d)
    print j
    
    
stovesensor_data.close()