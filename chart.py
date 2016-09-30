#!/usr/bin/python

import fusionCharts
import MySQLdb
import cgi
import os
import passwords

def create_chart(data, div_id="chart"):
    chart = fusionCharts.fusionChart(chart_type="multi_stacked_area", width=728, height=319)
    chart.color_array = []
    
    label_step = len(data)/10
    if (label_step < 1):
        label_step = 1
    chart.setChartTagAttributes({"caption":"Stove Temperature", "labelStep":label_step})
    chart.addDataSeries("Temperature", data, 
                        series_attributes = {"renderAs":"column", "showValues":"0", "alpha":70})
    html = chart.getHTML(div_id)
    return html

def get_temperatures():
    data = {}
    db = MySQLdb.connect("localhost", "gassensor", passwords.sql(), "gas")
    cursor = db.cursor()
    db_data = get_temperature_data(cursor, db)
    for row in db_data:
        temperature = row[0]
        time = row[1]
        time = time.strftime("%I:%M %p, %m/%d/%y")
        data[time] = temperature
    return data
        
    
def get_temperature_data(cursor, db):
    run = "SELECT temperature, time from gas.temperatures order by time desc limit 100"
    cursor.execute(run)
    result = cursor.fetchall()
    return result

def print_html():
    print "Content-type: text/html\n\n"
    print "<script src='/fusioncharts/js/fusioncharts.js'></script>"
    print "<html>"
    data = get_temperatures()
    print create_chart(data) + "</html>"