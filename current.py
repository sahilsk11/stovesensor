import glob
import time
import MySQLdb
import datetime
import passwords
import notification
import pprint

numbers = [{"number":passwords.number(), "provider":'tmomail.net'}]

db = MySQLdb.connect("localhost", "gassensor", passwords.sql(), "gas")
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
    get_information = "SELECT " + column + " from gas." + table + " order by time desc limit " + values
    cursor.execute(get_information)
    previous = cursor.fetchone()
    if (previous == None):
        return None
    return previous[0]
    
def upload_estimate(type, temperature):
    previous = get_value("calculated", "status", 1)
    if (previous == None or previous != type):
        time = datetime.datetime.now()
        script = "insert into calculated (status, time, temperature) values ('%s', '%s', '%d')" % (type, time, temperature)
        cursor.execute(script)
        db.commit()

def gas_on(temperature):
    last_value = get_value("temperatures", "temperature", 1) #return the last calculated value
    last_on = get_value("calculated", "time", 1)
    #Check for last temperature change
    if (last_value != None):
        #Temperature went down by 3 degrees
        if (temperature - last_value >= 3):
            return ("MAYBE", "none")
        #Temperature went up by 5 degrees
        if (last_value - temperature >= 5):
            return ("ON", last_on)
    #Temperature above 100
    if (temperature > 100):
        return ("ON", last_on)
    #Temperature between 100 and 80, but will happen if previous conditions are false
    if (temperature <= 100 and temperature >= 80):
        return ("MAYBE", "none")
    #Temperature below 80
    if (temperature < 80):
            return ("OFF", "none")

def gas_left_on(temperature):
    if (gas_on(temperature)):
        last_value = get_value("calculated", "status", 1)
        if (last_value[0] == "ON"):
            on_time = get_value("calculated", "time", 1)
            if (datetime.datetime.now() - datetime.timedelta(minutes=20) > on_time):
                return (True, on_time)
    return (False, None)

def send_notifications(users):
    for user in range (0, len(users)):
        n = notification.notification(user["number"], user["provider"])
        n.send_email()

while True:
    temperature_f = read_temp()[1]
    upload_value(temperature_f)
    print(temperature_f)
    type = gas_on(temperature_f)[0]
    upload_estimate(type, temperature_f)
    print type
    if (gas_left_on(temperature_f)[0]):
        send_notifications(numbers)
    time.sleep(30)