# Asset Monitoring Dashboard 1.0
# Cisco Meraki IoT + Cisco Industrial Asset Vision
# MIT License, flopach / Cisco Systems 2021

# ================================= #
#          GLOBAL Settings          #
# ================================= #
# Configure before building up and running docker-compose
# Select 1 to enable or 0 to DISable data collection for Meraki MT sensors or Industrial Asset Vision
meraki = 1
asset_vision = 1


# ================================= #
#          Meraki Settings          #
# ================================= #
base_url = "https://api.meraki.com/api/v1"
meraki_api_key = ""
network_id = "" #easily get it via https://developer.cisco.com/meraki/api-v1/#!get-organization-networks

# serial numbers of your sensors
# these are lists!
# example ["xxxx-xxxx-xxx","xxxx-xxxx-xxx","xxxx-xxxx-xxx"] or leave empty []
temperature_sensors = [] 
door_sensors = []
waterleak_sensors = []


# ================================= #
#        IAV MQTT Settings          #
# ================================= #
# Edit here your MQTT parameters from your MQTT broker
# You can also use Mosquitto locally
# At first you must set a MQTT broker in IAV
mqtt_server = "" # just write here "mosquitto" when using the local mosquitto from docker-compose
mqtt_port = 1883
mqtt_client_id = ""
mqtt_username = ""
mqtt_password = ""
mqtt_subscribe = "/#" # use # to subscribe to all topics


# ================================= #
### DO NOT EDIT! ###
# static config data for InfluxDB 
# InfluxDB
influx_token = "sensordata_token123"
influx_org = "sensordata_organization"
influx_bucket = "sensordata_bucket"
influx_url = "http://influxdb:8086"