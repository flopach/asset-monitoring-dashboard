# Asset Monitoring Dashboard 1.1
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

	try:
		rawjson = msg.payload.decode('utf-8')
		data = json.loads(rawjson)
		print(data) #uncomment for troubleshooting

		try:			
			# create dictionary which will be written to influxDB
			data_to_write = { "measurement": data["name"],
							  "tags" : { "serialNumber": data["serialNumber"] },
							  "fields" : {},
							  "time" : data["timestamp"]
							}
			
			for sensortype in data["telemetry"]:
				data_to_write["fields"][sensortype] = data["telemetry"][sensortype]["value"]

			if "name" in data["asset"]:
				data_to_write["tags"]["asset_name"] = data["asset"]["name"]

			# Write data to influxDB with MS precision timestamp
			influxdb_connect.write_api.write(bucket=config.influx_bucket,org=config.influx_org,record=data_to_write,write_precision=influxdb_connect.WritePrecision.MS)

		except Exception as e:
			print("Can't write to database: {}".format(e))

	except Exception as e:
		print("MQTT Message Error: {}".format(e))

def main():
	print("Starting MQTT Client")
	# MQTT connection parameters
	if config.mqtt_client_id == "":
		config.mqtt_client_id = "py_connector"
	client = mqtt.Client(client_id=config.mqtt_client_id, protocol=mqtt.MQTTv311, transport="tcp")
	client.on_connect = on_connect
	client.on_disconnect = on_disconnect
	client.on_log = on_log
	client.on_message = on_message

	if config.mqtt_username != "" or config.mqtt_username != "":
		client.username_pw_set(config.mqtt_username, config.mqtt_password)
	client.connect(host=config.mqtt_server, port=config.mqtt_port, keepalive=60)
	client.loop_forever()