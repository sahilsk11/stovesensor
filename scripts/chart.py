#!/usr/bin/python

import fusionCharts
import MySQLdb
import cgi
import os
import passwords

def getSize(width):
    if (width > 1000):
        return "50"
    elif (width > 930):
        return "120"
    return "150"

def create_chart(data, values, div_id="chart"):
    chart = fusionCharts.fusionChart(chart_type="multi_stacked_area", width="100%", height="100%")
    chart.color_array = []
    
    label_step = values
    chart.setChartTagAttributes({"caption":"Stove Temperature", "labelStep":label_step, "theme":"fint", "anchorRadius":1, "anchorBorderThickness":0})
    chart.addDataSeries("Temperature", data, 
                        series_attributes = {"renderAs":"column", "showValues":"0", "alpha":70})
    html = chart.getHTML(div_id, js_only=1)
    return html

def get_temperatures():
    data = {}
    db = MySQLdb.connect("localhost", "stovesensor", passwords.sql(), "stovedata")
    cursor = db.cursor()
    db_data = get_temperature_data(cursor, db)
    i = 0
    while (i < len(db_data)):
        row = db_data[i]
        temperature = row[0]
        time = row[1]
        time = time.strftime("%m/%d %H:%M %p")
        data[time] = temperature
        i += 1
    return data
        
    
def get_temperature_data(cursor, db):
    run = "SELECT temperature, time from stovedata.temperatures order by time desc limit 120"
    cursor.execute(run)
    result = cursor.fetchall()
    return result

print "Content-type: text/html\n\n"

form = cgi.FieldStorage()
width = form.getfirst("width", "")
int_width = int(width)
values = getSize(int_width)
data = get_temperatures()
print create_chart(data, values)