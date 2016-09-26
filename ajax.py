#!/usr/bin/python

print "Content-type: application/json\n\n"

import operations
import cgi
import json
import datetime
import current

form = cgi.FieldStorage()
page_load = form.getfirst("pageload", "")

temperature = current.read_temp()[1]

if (page_load != ""):
    (status, time) = current.gas_on(temperature)
    d = {"temperature":temperature, "status": status, "on_time":time}
    j = json.dumps(d)
    print j
    
