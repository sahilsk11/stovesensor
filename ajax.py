#!/usr/bin/python

print "Content-type: application/json\n\n"

import cgi
import json
import datetime
import current

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
    d = {"temperature":temperature, "status": status, "on_time":on_time}
    j = json.dumps(d)
    print j
    
