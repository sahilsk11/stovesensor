import glob
import time
import MySQLdb
import datetime
import passwords
import notification
from datetime import date
import shelve
import requests

stove_info = shelve.open("uid.shelve")
if (not "uid" in stove_info):
    stove_info["uid"] = 2468
code = stove_info["uid"]

numbers = [{"number":passwords.number(), "provider":'tmomail.net'}]

db = MySQLdb.connect("localhost", "stovesensor", passwords.sql(), "stovedata")
cursor = db.cursor()
recent_on = 0
 
base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'
 
def read_temp_raw():
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines
 
def read_temp():
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        temp_f = temp_c * 9.0 / 5.0 + 32.0
        return temp_c, temp_f
    
def upload_value(temperature):
    time = datetime.datetime.now()
    script = "insert into temperatures (temperature, time) values ('%d', '%s')" % (temperature, time)
    cursor.execute(script)
    db.commit()
    
def get_value(table, column, values):
    values = str(values)
    get_information = "SELECT " + column + " from stovedata." + table + " order by time desc limit " + str(values)
    cursor.execute(get_information)
    values = int(values)
    previous = cursor.fetchmany(values)
    if (previous == None):
        return None
    if (len(previous) > 1):
        return(previous[0][0], previous[1][0])
    return previous[0][0]
    
def upload_estimate(type, temperature):
    previous = get_value("calculated", "status", 1)
    if (previous == None or previous != type):
        time = datetime.datetime.now()
        script = "insert into calculated (status, time, temperature) values ('%s', '%s', '%d')" % (type, time, temperature)
        cursor.execute(script)
        db.commit()

def upload_notification(type):
    time = datetime.datetime.now()
    script = "insert into Notifications (type, time) values ('%s', '%s')" % (type, time)
    cursor.execute(script)
    db.commit()

def gas_on(temperature):
    last_value = get_value("temperatures", "temperature", 2)[1] #return the last calculated value
    last_on = get_value("calculated", "time", 1)
    #Check for last temperature change
    if (last_value != None):
        #Temperature went down by 3 degrees
        if (last_value - temperature >= 3):
            print("temperature went down by 3")
            return ("MAYBE", "none")
        #Temperature went up by 5 degrees
        if (temperature - last_value >= 5):
            print("temperature went up by 5")
            return ("ON", last_on)
    #Temperature above 100
    if (temperature > 100):
        return ("ON", last_on)
    #Temperature between 100 and 90, but will happen if previous conditions are false
    if (temperature <= 100 and temperature >= 90):
        return ("MAYBE", "none")
    #Temperature below 80
    if (temperature < 80):
            return ("OFF", "none")

def gas_left_on(temperature, status, time=20):
    if (status == "ON"):
        last_value = get_value("calculated", "status", 1)
        if (last_value == "ON"):
            on_time = get_value("calculated", "time", 1)
            if (datetime.datetime.now() - datetime.timedelta(minutes=time) > on_time):
                return (True, on_time)
    return (False, None)

def send_notifications(users):
    for user in users:
        n = notification.notification(str(user["number"]), user["provider"])
        n.send_email()
        n.close_shelf()

def can_send_notification():
    #last_time = get_value("Notifications", "time", 1)
    #last_type = get_value("Notifications", "type", 1)
    #if (last_time == None or (last_time + datetime.timedelta(minutes=20) < datetime.datetime.now())):
    #    return True
    #return False
    return True

def upload_data():
    temperature = get_value("temperatures", "temperature", 1)
    status = get_value("calculated", "status", 1)
    if (status == "ON"):
        on_time = get_value("calculated", "time", 1)
        on_time = on_time.strftime("%I:%M %p")
    else:
        on_time = "none"
    time = get_value("temperatures", "time", 1)
    time = time.strftime("%I:%M %p on %m/%d/%y")
    d = {"temperature":temperature, "status": status, "on_time":on_time, "update_time":time, "code":code}
    data = str(d)
    headers = {"code":code, "data":data, "command":"upload"}
    response = requests.post("https://www.iotspace.tech/stovesensor/scripts/data_storage.py", data=headers)

if (__name__ == "__main__"):
    temperature_f = read_temp()[1]
    upload_value(temperature_f)
    print(temperature_f)
    type = gas_on(temperature_f)[0]
    upload_estimate(type, temperature_f)
    print type
    upload_data()
    if (gas_left_on(temperature_f, type, 3)[0] and can_send_notification()):
        send_notifications(numbers)
stove_info.close()