# Asset Monitoring Dashboard 1.0
# Cisco Meraki IoT + Cisco Industrial Asset Vision
# MIT License, flopach / Cisco Systems 2021

import paho.mqtt.client as mqtt
import time
import json
import config
import influxdb_connect
from datetime import datetime

def on_connect(client, userdata, flags, rc):
	""" When connected: """
	print(f"Connected with result code {rc}")
	#subscribe here to your MQTT topics
	client.subscribe(config.mqtt_subscribe)

def on_disconnect(client, userdata, flags, rc=0):
	""" On disconnect """
	print(f"Disconnected with result code {rc}")

def on_log(client, userdata, level, buf):
	""" Print logs """
	print("log: " + buf)

def on_message(client, userdata, msg):
	"""
	The callback for when a PUBLISH message is received from the server.
	"""
	rawjson = msg.payload.decode('utf-8')
	data = json.loads(rawjson)
	#print(data) #uncomment for troubleshooting
	
	try: 
		# Temperature + Humidity
		# AV200, AV201, AV203
		if "temperature" in data["telemetry"] and "humidity" in data["telemetry"]:
			try:
				influxdb_connect.write_api.write(
					bucket=config.influx_bucket,
					org=config.influx_org,
					record=influxdb_connect.Point(data["name"])
					.tag("asset_name", data["asset"]["name"])
					.field("temperature",float(data["telemetry"]["temperature"]["value"]))
					.field("humidity",float(data["telemetry"]["humidity"]["value"]))
					.time(datetime.fromtimestamp(data["timestamp"]/1000).strftime("%Y/%m/%d %I:%M:%S %p")))
			except Exception as e:
				print("Can't write to database: {}".format(e))

		# Occupancy Sensor
		# AV207
		elif  "occupied" in data["telemetry"] and "illuminance" in data["telemetry"]:
			try:
				influxdb_connect.write_api.write(
					bucket=config.influx_bucket,
					org=config.influx_org,
					record=influxdb_connect.Point(data["name"])
					.tag("asset_name", data["asset"]["name"])
					.field("temperature",float(data["telemetry"]["temperature"]["value"]))
					.field("illuminance",int(data["telemetry"]["illuminance"]["value"]))
					.field("occupancy",data["telemetry"]["occupied"]["value"])
					.time(datetime.fromtimestamp(data["timestamp"]/1000).strftime("%Y/%m/%d %I:%M:%S %p")))
			except Exception as e:
				print("Can't write to database: {}".format(e))

		# Water Leak Sensor
		# AV205
		elif "waterLeak" in data["telemetry"]:
			try:
				influxdb_connect.write_api.write(
					bucket=config.influx_bucket,
					org=config.influx_org,
					record=influxdb_connect.Point(data["name"])
					.tag("asset_name", data["asset"]["name"])
					.field("waterleak", data["telemetry"]["waterLeak"]["value"])
					.time(datetime.fromtimestamp(data["timestamp"]/1000).strftime("%Y/%m/%d %I:%M:%S %p")))
			except Exception as e:
				print("Can't write to database: {}".format(e))

		# Door/Window Sensor
		# AV204
		elif "doorOpen" in data["telemetry"]:
			try:
				influxdb_connect.write_api.write(
					bucket=config.influx_bucket,
					org=config.influx_org,
					record=influxdb_connect.Point(data["name"])
					.tag("asset_name", data["asset"]["name"])
					.field("doorStatus", data["telemetry"]["doorOpen"]["value"])
					.time(datetime.fromtimestamp(data["timestamp"]/1000).strftime("%Y/%m/%d %I:%M:%S %p")))
			except Exception as e:
				print("Can't write to database: {}".format(e))

		# Light Level Sensor
		# AV206
		elif "illuminance" in data["telemetry"]:
			try:
				influxdb_connect.write_api.write(
					bucket=config.influx_bucket,
					org=config.influx_org,
					record=influxdb_connect.Point(data["name"])
					.tag("asset_name", data["asset"]["name"])
					.field("illuminance",int(data["telemetry"]["illuminance"]["value"]))
					.time(datetime.fromtimestamp(data["timestamp"]/1000).strftime("%Y/%m/%d %I:%M:%S %p")))
			except Exception as e:
				print("Can't write to database: {}".format(e))
		
		# Machine Temperature Sensor
		# AV250
		elif "temperature"  in data["telemetry"]:
			try:
				influxdb_connect.write_api.write(
					bucket=config.influx_bucket,
					org=config.influx_org,
					record=influxdb_connect.Point(data["name"])
					.tag("asset_name", data["asset"]["name"])
					.field("temperature",float(data["telemetry"]["temperature"]["value"]))
					.time(datetime.fromtimestamp(data["timestamp"]/1000).strftime("%Y/%m/%d %I:%M:%S %p")))
			except Exception as e:
				print("Can't write to database: {}".format(e))

		else:
			print("MQTT Data Error - could not find any existing configuration for inserting to Influx (GPS sensors are not yet supported).")
	except Exception as e:
		print("Can't parse the message: {}".format(e))

def main():
	print("Starting MQTT Client")
	# MQTT connection parameters
	if config.mqtt_client_id == "":
		config.mqtt_client_id = "py_connector"
	client = mqtt.Client(client_id=config.mqtt_client_id, protocol=mqtt.MQTTv311, transport="tcp")
	client.on_connect = on_connect
	client.on_disconnect = on_disconnect
	#client.on_log = on_log
	client.on_message = on_message

	if config.mqtt_username != "" or config.mqtt_password != "":
		client.username_pw_set(config.mqtt_username, config.mqtt_password)
	client.connect(host=config.mqtt_server, port=config.mqtt_port, keepalive=60)
	client.loop_forever()
