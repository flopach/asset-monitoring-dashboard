# Asset Monitoring Dashboard 1.0
# Cisco Meraki IoT + Cisco Industrial Asset Vision
# MIT License, flopach / Cisco Systems 2021

import paho.mqtt.client as mqtt
import time
import json
import config
import influxdb_connect

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

	# Temperature + Humidity
	# AV200, AV201, AV203
	if "data_temperature" in data["payload"] and "data_humidity" in data["payload"]:

		try:
			influxdb_connect.write_api.write(
				bucket=config.influx_bucket,
				org=config.influx_org,
				record=influxdb_connect.Point(data["metadata"]["sensorName"])
				.tag("asset_name", data["metadata"]["assetName"])
				.field("temperature",data["payload"]["data_temperature"])
				.field("humidity",data["payload"]["data_humidity"])
				.time(data["metadata"]["timestamp"]))
		except Exception as e:
			print("Can't write to database: {}".format(e))
	
	# Occupancy Sensor
	# AV207
	elif  "data_occupancy" in data["payload"] and "data_illuminance" in data["payload"]:
		
		try:
			if data["payload"]["data_occupancy"] == "available":
				occupancy = 1
			elif data["payload"]["data_occupancy"] == "occupied":
				occupancy = 0
			else:
				occupancy = 404

			influxdb_connect.write_api.write(
				bucket=config.influx_bucket,
				org=config.influx_org,
				record=influxdb_connect.Point(data["metadata"]["sensorName"])
				.tag("asset_name", data["metadata"]["assetName"])
				.field("temperature",data["payload"]["data_temperature"])
				.field("illuminance",data["payload"]["data_illuminance"])
				.field("occupancy",occupancy)
				.time(data["metadata"]["timestamp"]))
		except Exception as e:
			print("Can't write to database: {}".format(e))

	# Water Leak Sensor
	# AV205
	elif "data_waterLeak" in data["payload"]:
		
		try:
			if data["payload"]["data_waterLeak"] == True:
				waterLeak = 1
			elif data["payload"]["data_waterLeak"] == False:
				waterLeak = 0
			else:
				waterLeak = 404

			influxdb_connect.write_api.write(
				bucket=config.influx_bucket,
				org=config.influx_org,
				record=influxdb_connect.Point(data["metadata"]["sensorName"])
				.tag("asset_name", data["metadata"]["assetName"])
				.field("waterleak",waterLeak)
				.time(data["metadata"]["timestamp"]))
		except Exception as e:
			print("Can't write to database: {}".format(e))

	# Door/Window Sensor
	# AV204
	elif "data_doorStatus" in data["payload"]:
		
		try:
			if data["payload"]["data_doorStatus"] == "open":
				doorStatus = 1
			elif data["payload"]["data_doorStatus"] == "closed":
				doorStatus = 0
			else:
				doorStatus = 404
			
			influxdb_connect.write_api.write(
				bucket=config.influx_bucket,
				org=config.influx_org,
				record=influxdb_connect.Point(data["metadata"]["sensorName"])
				.tag("asset_name", data["metadata"]["assetName"])
				.field("doorStatus",doorStatus)
				.time(data["metadata"]["timestamp"]))
		except Exception as e:
			print("Can't write to database: {}".format(e))

	# Light Level Sensor
	# AV206
	elif "data_illuminance" in data["payload"]:
		
		try:
			influxdb_connect.write_api.write(
				bucket=config.influx_bucket,
				org=config.influx_org,
				record=influxdb_connect.Point(data["metadata"]["sensorName"])
				.tag("asset_name", data["metadata"]["assetName"])
				.field("illuminance",data["payload"]["data_illuminance"])
				.time(data["metadata"]["timestamp"]))
		except Exception as e:
			print("Can't write to database: {}".format(e))

	else:
		print("MQTT Data Error - could not find any existing configuration for inserting to Influx (GPS sensors are not yet supported).")

def main():
	print("Starting MQTT Client")
	# MQTT connection parameters
	client = mqtt.Client(client_id=config.mqtt_client_id, protocol=mqtt.MQTTv311, transport="tcp")
	client.on_connect = on_connect
	client.on_disconnect = on_disconnect
	#client.on_log = on_log
	client.on_message = on_message

	client.username_pw_set(config.mqtt_username, config.mqtt_password)
	client.connect(host=config.mqtt_server, port=config.mqtt_port, keepalive=60)
	client.loop_forever()