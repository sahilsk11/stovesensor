# Stove Sensor
### Never leave your stove on again.

## About Stove Sensor
Stove sensor is a Raspberry Pi project that analyzes the temperature of your stove, and notifies users if their stove has been left on for an extended period of time. Additionally, it allows users to check on their stove from any smartphone or laptop. This means you never have to ask "Did I leave the gas on?" again.

##How it Works
A temperature sensor attached to the Raspberry Pi periodically collects the temperature, ands adds it to an SQL database. It then uses an algorithm based off previous temperatures and patterns to determine if the stove is on or off. Finally, it publishes all of this information to the SQL database. \n
In the scenario where the stove was left on, it sends a text message to the users alerting them.

## Made Using...
Python for all of back-end, including temperature monitoring, SQL information publishing, Amazon Web Services for server, and HTML, CSS, and JS for front-end.
