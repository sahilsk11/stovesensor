import MySQLdb
import requests
import shelve

shelf = shelve.open("stove_data.shelve", writeback= True)
shelf["user_info"] = []
shelf["uid"] = ""
shelf["last_sent"] = 0

headers = {"command":"newdevice"}
response = requests.get("https://www.iotspace.tech/stovesensor/status/scripts/data_storage.py", params=headers)
code = response.json()["new_code"]

shelf["uid"] = code

db = MySQLdb.connect("localhost", "stovesensor", passwords.sql(), "stovedata")
cursor = db.cursor()

script = "DELETE * FROM calculated"
cursor.execute(script)

script = "DELETE * FROM temperatures"
cursor.execute(script)

shelf.close()