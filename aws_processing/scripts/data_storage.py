#!/usr/bin/python

print "Content-type: application/json\n\n"

import shelve
import json
import cgi

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
    print {"success":True}
    print(stovesensor_data)
    
if (command == "pageload"):
    data = stovesensor_data["devices"][code]
    j = json.dumps(data)
    print j
    
stovesensor_data.close()