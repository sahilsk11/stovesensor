import glob
import time
import MySQLdb
import datetime
import passwords
import shelve
import requests

stove_info = shelve.open("stove_data.shelve", writeback=True)
if not ("user_info" in stove_info):
    stove_info["user_info"] = []
if not ("on_timer" in stove_info):
    stove_info["on_timer"] = 20

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

def gas_on(temperature):
    last_value = get_value("temperatures", "temperature", 2)[1] #return the last calculated value
    last_on = get_value("calculated", "time", 1)
    if (temperature > 105):
            return ("ON", last_on)
    #Check for last temperature change
    if (last_value != None):
        #Temperature above 105
        #Temperature went down by 7 degrees
        if (last_value - temperature >= 7):
            print("temperature went down by 7")
            return ("MAYBE", "none")
        #Temperature went up by 5 degrees
        if (temperature - last_value >= 5):
            print("temperature went up by 5")
            return ("ON", last_on)
    #Temperature between 100 and 90, but will happen if previous conditions are false
    if (temperature <= 100 and temperature >= 90):
        return ("MAYBE", "none")
    #Temperature below 90
    
    return ("OFF", "none")

def gas_left_on(temperature, status):
    if (status == "ON"):
        last_value = get_value("calculated", "status", 1)
        if (last_value == "ON"):
            on_time = get_value("calculated", "time", 1)
            if (datetime.datetime.now() - datetime.timedelta(minutes=stove_info["on_timer"]) > on_time):
                return (True, on_time)
    return (False, None)

def can_send_notification():
    if (not "last_sent" in stove_info):
        stove_info["last_sent"] = 0
    last_time = stove_info["last_sent"]
    if (last_time == 0 or last_time + datetime.timedelta(minutes=5) < datetime.datetime.now()):
        stove_info["last_sent"] = datetime.datetime.now()
        return True
    else:
        return False

def average_of_temperature(hours=3):
    script = "SELECT AVG(temperature) FROM temperatures where date > date_sub(now() - interval " + str(hours) + " hours"
    cursor.execute(script)
    db.commit()

def upload_data(temperature_f, type):
    temperature = get_value("temperatures", "temperature", 1)
    status = get_value("calculated", "status", 1)
    if (status == "ON"):
        on_time = get_value("calculated", "time", 1)
        on_time = on_time.strftime("%I:%M %p")
    else:
        on_time = "none"
    time = get_value("temperatures", "time", 1)
    time = time.strftime("%I:%M %p on %m/%d/%y")
    send_notification = False
    if (gas_left_on(temperature_f, type)[0] and can_send_notification()):
        send_notification = True
    if (not "uid" in stove_info):
        print("setting code")
    print(datetime.datetime.now())
    code = stove_info["uid"]
    print(code)
    d = {"temperature":temperature, "status": status, "on_time":on_time, "update_time":time, "code":code, "notification":send_notification, "numbers":stove_info["user_info"]}
    data = str(d)
    print(data)
    headers = {"code":code, "data":data, "command":"upload"}
    response = requests.post("https://www.iotspace.tech/stovesensor/status/scripts/data_storage.py", data=headers)

if (__name__ == "__main__"):
    temperature_f = read_temp()[1]
    upload_value(temperature_f)
    print(temperature_f)
    type = gas_on(temperature_f)[0]
    upload_estimate(type, temperature_f)
    print type
    upload_data(temperature_f, type)
    print "\n"
stove_info.close()