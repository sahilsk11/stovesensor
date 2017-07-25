#!/usr/bin/python

import fusionCharts
import MySQLdb
import cgi
import os
import passwords

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

def get_temperatures():
    data = {}
    db = MySQLdb.connect("localhost", "stovesensor", passwords.sql(), "stovedata")
    cursor = db.cursor()
    db_data = get_temperature_data(cursor, db)
    alternate = 1
    if (len(db_data) >= 330):
        alternate = 30
    elif (len(db_data) >= 110):
        alternate = 10
    elif (len(db_data) >= 55):
        alternate = 5
    for row in db_data:
        temperature = row[0]
        time = row[1]
        time = time.strftime("%I:%M %p, %m/%d/%y")
        data[time] = temperature
    return data
        
    
def get_temperature_data(cursor, db):
    run = "SELECT temperature, time from stovedata.temperatures order by time desc limit 1500"
    cursor.execute(run)
    result = cursor.fetchall()
    return result

print "Content-type: text/html\n\n"
data = get_temperatures()
print create_chart(data)