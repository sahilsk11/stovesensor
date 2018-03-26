import glob
import time
import MySQLdb
import datetime
import passwords
import shelve
import requests
import led_control


#initialize shelve data with structure
stove_info = shelve.open("stove_data.shelve", writeback=True)
if not ("user_info" in stove_info):
    stove_info["user_info"] = []
if not ("on_timer" in stove_info):
    stove_info["on_timer"] = 30
if not ("interval" in stove_info):
    stove_info["interval"] = 60   
code = stove_info["uid"]

#connect to Raspi server
db = MySQLdb.connect("localhost", "stovesensor", passwords.sql(), "stovedata")
cursor = db.cursor()
#FIX
recent_on = 0

#generate new device code
def new_id():
    headers = {"command":"newdevice"}
    response = requests.get("https://www.iotspace.tech/stovesensor/status/scripts/data_storage.py", params=headers)
    #save to device
    new_id = response.json()["new_id"]
    return new_id
 
#default function to read temperature data from sensor
def read_temp_raw():
    base_dir = '/sys/bus/w1/devices/'
    device_folder = glob.glob(base_dir + '28*')[0]
    device_file = device_folder + '/w1_slave'
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines

#Decodes the readings from sensor to human-readable format
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
    
#save the value of temperature to SQL database
def save_temperature_value(value, table="temperatures", type="temperature"):
    time = datetime.datetime.now()
    script = "insert into " + table + " ("+type+", time) values ('%d', '%s')" % (value, time)
    cursor.execute(script)
    db.commit()

#return a set number of values from the db
#return FIX THIS
def fetch_values(table, column, values):
    values = str(values)
    get_information = "SELECT " + column + " from stovedata." + table + " order by time desc limit " + str(values)
    cursor.execute(get_information)
    values = int(values)
    previous = cursor.fetchmany(values)
    if (previous == None  or len(previous) == 0):
        return None
    if (len(previous) > 1):
        return(previous[0][0], previous[1][0])
    return previous[0][0]
    
#Upload a new value IF the type changed
#Type would be 'ON', 'OFF', or 'MAYBE'
def upload_estimate(type, temperature):
    #Return the last value to check if type changed
    previous = fetch_values("calculated", "status", 1)
    if (previous == None or previous != type):
        time = datetime.datetime.now()
        script = "insert into calculated (status, time, temperature) values ('%s', '%s', '%d')" % (type, time, temperature)
        cursor.execute(script)
        db.commit()

#Core of the device
#Calculated whether the stove is on or not
#This method is constantly updated after tests are conducted
def gas_on(temperature, average):
    last_value = fetch_values("temperatures", "temperature", 2)[1] #return the last calculated value
    last_on = fetch_values("calculated", "time", 1)
    
    if (temperature < 70 or temperature <= average+2):
        print("Less than 70/average")
        return ("OFF", "none")
    #Check for last temperature change
    if (last_value == None):
        last_value = temperature
    #Temperature went down by 3 degrees
    if (last_value - temperature >= 7):
        print("temperature went down by 3")
        return ("MAYBE", "none")
    if (temperature >= average+10):
        #Test corner case of low average
        if (average <= 65 and temperature < 80):
            #Check if temperature is increasing with average
            if (temperature - last_value > 7):
                #Greater than average and went up by 3
                print("Greater than average and increasing")
                return ("ON", last_on)
            #If low average and not rising, stove is off
            else:
                print("Average is low and temperature is not rising significantly")
        
        if (last_value - temperature > 5):
            print("Greater than average and decreasing")
            return ("MAYBE", "none")
        if (temperature >= last_value - 3):
            #Greater than average final case
            print("Greater than average and increasing")
            return ("ON", last_on)
    if (temperature > 105):
        #Temperature above 105
        print("Greater than 105")
        return ("ON", last_on)
    if (last_value != None):
        #Temperature went up by 5 degrees
        if (temperature - last_value >= 5):
            print("temperature went up by 5")
            return ("ON", "none")
    
    #Temperature between 100 and 90, but will happen if previous conditions are false
    if (temperature <= 100 and temperature >= 90):
        print("between 90 and 100")
        return ("MAYBE", "none")
    #Temperature below 90
    return ("OFF", "none")

#determine if the stove is left on
def gas_left_on(temperature, status):
    #check the last status
    if (status == "ON"):
        #Pull status and time in 1 call
        last_value = fetch_values("calculated", "status", 1)
        #This ensures the stove has been on ever since the last time it changed
        if (last_value == "ON"):
            on_time = fetch_values("calculated", "time", 1)
            if (datetime.datetime.now() - datetime.timedelta(minutes=stove_info["on_timer"]) > on_time):
                return (True, on_time)
    return (False, None)

#Based on the last time a notification was sent, determine if next is appropriate
def can_send_notification():
    if (not "last_sent" in stove_info):
        stove_info["last_sent"] = 0
    last_time = stove_info["last_sent"]
    if (last_time == 0 or last_time + datetime.timedelta(minutes=stove_info["interval"]) < datetime.datetime.now()):
        stove_info["last_sent"] = datetime.datetime.now()
        return True
    else:
        return False

def average_of_temperature(hours=3):
    script = "SELECT AVG(temperature) FROM temperatures where time > date_sub(now(), interval " + str(hours) + " hour)"
    cursor.execute(script)
    db.commit()
    data = cursor.fetchone()
    return round(float(data[0]), 2)

def pushto_server(temperature_f, type):
    temperature = fetch_values("temperatures", "temperature", 1)
    status = fetch_values("calculated", "status", 1)
    if (status == "ON"):
        on_time = fetch_values("calculated", "time", 1)
        on_time = on_time.strftime("%I:%M %p")
    else:
        on_time = "none"
    time = fetch_values("temperatures", "time", 1)
    time = time.strftime("%I:%M %p on %m/%d/%y")
    send_notification = False
    if (gas_left_on(temperature_f, type)[0] and can_send_notification()):
        send_notification = True
    if (not "uid" in stove_info):
        print("setting code")
    print(datetime.datetime.now())
    print(code)
    d = {"temperature":temperature, "status": status, "on_time":on_time, "update_time":time, "code":code, "notification":send_notification, "numbers":stove_info["user_info"]}
    data = str(d)
    print(data)
    headers = {"code":code, "data":data, "command":"upload"}
    try:
        response = requests.post("https://www.iotspace.tech/stovesensor/status/scripts/data_storage.py", data=headers)
    except requests.ConnectionError:
        return False
    return True

if (__name__ == "__main__"):
    led = led_control.RGBled()
    if (code == None or code == ""):
        stove_info["uid"] = new_id()
        code = stove_info["uid"]
    temperature_f = read_temp()[1]
    save_temperature_value(temperature_f)
    print(temperature_f)
    average = average_of_temperature()
    print(average)
    type = gas_on(temperature_f, average)[0]
    upload_estimate(type, temperature_f)
    print type
    upload_complete = pushto_server(temperature_f, type)
    led.color_green()
    time.sleep(0.1)
    if (not upload_complete):
        #cannot connect to internet
        led.color_blue()
        led.color_red(exclusive=False)
    else:
        if (type == "ON"):
            led.color_red()
        elif (type == "MAYBE"):
            led.color_blue()
        else:
            led.off()
    print "\n"
stove_info.close()