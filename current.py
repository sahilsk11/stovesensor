import glob
import time
import MySQLdb
import datetime
import passwords
from distutils.command.upload import upload



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
    get_information = "SELECT * from gas." + table + " order by " + column + " desc limit " + values
    cursor.execute(get_information)
    previous = cursor.fetchone()
    return previous
    
def upload_estimate(type, temperature):
    previous = get_value("calculated", "time", 1)
    if (previous != None):
        if (previous != type):
            time = datetime.datetime.now()
            script = "insert into calculated (status, time, temperature) values ('%s', '%s', '%d')" % (type, time, temperature)
            cursor.execute(script)
            db.commit()
    
def gas_on(temperature):
    last_value = get_value("calculated", "time", 1) #return the last calculated value
    if (last_value == None):
        return False
    print last_value
    

while True:
    temperature_f = read_temp()[1]
    upload_value(temperature_f)
    print(temperature_f)
    print(gas_on(temperature_f))
    upload_estimate("type", temperature)
    time.sleep(30)