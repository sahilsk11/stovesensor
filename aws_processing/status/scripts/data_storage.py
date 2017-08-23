#!/usr/bin/python

print "Content-type: application/json\n\n"

import shelve
import json
import cgi
import notification
import random
import datetime

log = open("log.txt", "a")
log.write("\n\nRunning at "+str(datetime.datetime.now()))

def send_notifications(code, users):
    for user in users:
        notification.send_notification(str(user["number"]), code)

stovesensor_data = shelve.open("stove_info.shelve", writeback=True)
if (not "devices" in stovesensor_data):
        stovesensor_data["devices"] = {}

form = cgi.FieldStorage()
command = form.getfirst("command", "")
code = form.getfirst("code", "")
data = form.getfirst("data", "")

log.write("command: " + command)

if (command == "upload"):
    json_data = eval(data)
    int_code = int(code)
    if (not int_code in stovesensor_data["devices"]):
        stovesensor_data["devices"] = {}
    stovesensor_data["devices"][int_code] = json_data
    if (json_data["notification"]):
        log.write("Sending notification to "+str(json_data["numbers"]))
        for number in json_data["numbers"]:
            notification.send_notification(number, code)
    print {"success":True}
    
if (command == "pageload"):
    int_code = int(code)
    data = stovesensor_data["devices"][int_code]
    j = json.dumps(data)
    print j
    
if (command == "newdevice"):
    completed = False
    while (not completed):
        uid = 0
        for i in range(0, 4):
            number = random.randint(1, 9)
            uid = uid * 10 + number
            str_number = str(uid)
        str_number = str(uid)
        counter = str_number.count("6")
        if (uid not in stovesensor_data["devices"] and counter < 3):
            stovesensor_data["devices"][uid] = {}
            completed = True
    d = {"success": True, "new_code":uid}
    log.write("New device with code " + str(uid))
    j = json.dumps(d)
    print j
    
log.close()
stovesensor_data.close()