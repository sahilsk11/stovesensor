#!/usr/bin/python

import fusionCharts
import MySQLdb
import cgi
import os
import passwords

def getSize(width):
    if (width > 1500):
        return "650"
    elif (width > 1190):
        return "1190"
    elif (width > 970):
        return "100"
    else:
        return "70"

def create_chart(data, div_id="chart"):
    chart = fusionCharts.fusionChart(chart_type="multi_stacked_area", width="100%", height="70%")
    chart.color_array = []
    
    label_step = len(data)/10
    if (label_step < 1):
        label_step = 1
    chart.setChartTagAttributes({"caption":"Stove Temperature", "labelStep":label_step})
    chart.addDataSeries("Temperature", data, 
                        series_attributes = {"renderAs":"column", "showValues":"0", "alpha":70})
    html = chart.getHTML(div_id, js_only=1)
    return html

def get_temperatures(values):
    data = {}
    db = MySQLdb.connect("localhost", "stovesensor", passwords.sql(), "stovedata")
    cursor = db.cursor()
    db_data = get_temperature_data(cursor, db, values)
    alternate = 1
    if (len(db_data) >= 330):
        alternate = 3
    elif (len(db_data) >= 110):
        alternate = 2
    elif (len(db_data) >= 55):
        alternate = 1
    i = 0
    while (i < len(db_data)):
        row = db_data[i]
        temperature = row[0]
        time = row[1]
        time = time.strftime("%I:%M %p, %m/%d/%y")
        data[time] = temperature
        i = i + alternate
    return data
        
    
def get_temperature_data(cursor, db, values):
    run = "SELECT temperature, time from stovedata.temperatures order by time desc limit 650"
    cursor.execute(run)
    result = cursor.fetchall()
    return result

print "Content-type: text/html\n\n"

form = cgi.FieldStorage()
width = form.getfirst("width", "")
values = getSize(width)
data = get_temperatures(values)
print create_chart(data)