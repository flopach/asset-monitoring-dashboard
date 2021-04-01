# Asset Monitoring Dashboard 1.1
# Cisco Meraki IoT + Cisco Industrial Asset Vision
# MIT License, flopach / Cisco Systems 2021

import requests
import config
import pandas as pd
import influxdb_connect
import time

def get_latest_sensor_reading(sensor_serial,metric):
	"""
	Get latest sensor reading from MT sensor
	metrics: 'temperature', 'humidity', 'water_detection' or 'door'
	"""
	headers = {
		"Content-Type": "application/json",
		"Accept": "application/json",
		"X-Cisco-Meraki-API-Key": config.meraki_api_key
	}

	params = {
		"serials[]" : sensor_serial,
		"metric" : metric
	}

	try:
		msg = requests.request('GET', f"{config.base_url}/networks/{config.network_id}/sensors/stats/latestBySensor", headers=headers, params=params)
		if msg.ok:
			data = msg.json()
			return data
	except Exception as e:
		print("API Connection error: {}".format(e))


def get_historical_sensor_reading(sensor_serial,metric,timespan,resolution):
	"""
	Get historical sensor readings from MT sensor
	The valid resolutions are: 1, 120, 3600, 14400, 86400. The default is 120.
	"""
	headers = {
		"Content-Type": "application/json",
		"Accept": "application/json",
		"X-Cisco-Meraki-API-Key": config.meraki_api_key
	}

	params = {
		"serials[]" : sensor_serial,
		"metric" : metric,
		"timespan" : timespan,
		"resolution" : resolution,
		"agg" : "max"
	}

	try:
		msg = requests.request('GET', f"{config.base_url}/networks/{config.network_id}/sensors/stats/historicalBySensor", headers=headers, params=params)
		if msg.ok:
			data = msg.json()
			return data
	except Exception as e:
		print("API Connection error: {}".format(e))


def get_sensor_name_mapping():
	"""
	Get the names of all Meraki MT sensors and map it to the serials numbers in a dictionary
	Will be used for inserting into the database
	"""
	headers = {
		"Content-Type": "application/json",
		"Accept": "application/json",
		"X-Cisco-Meraki-API-Key": config.meraki_api_key
	}

	try:
		msg = requests.request('GET', f"{config.base_url}/networks/{config.network_id}/sensors", headers=headers)
		data = msg.json()

		sensor_name_mapping = {}
		for s in data["sensors"]:
			sensor_name_mapping[s["serial"]] = s["name"]

		return sensor_name_mapping

	except Exception as e:
		print("API Connection error: {}".format(e))

def put_historical_data_into_influx_temp_hum(sensor_serial,timespan,resolution):
	"""
	Insert historical data into InfluxDB - temperature + humidity only
	Using the Meraki Dashboard API functions 
	"""
	try:
		# read temperature data + insert into dataframe
		temperature_readings = get_historical_sensor_reading(sensor_serial,"temperature",timespan,resolution)
		time.sleep(5)
		df = pd.DataFrame(temperature_readings[0]["data"])
		df = df.rename(columns={"ts":"ts","value":"temperature"})
		df = df.set_index("ts")

		# read humidity data + insert into dataframe
		humidity_readings = get_historical_sensor_reading(sensor_serial,"humidity",timespan,resolution)
		time.sleep(5)
		df_hum = pd.DataFrame(humidity_readings[0]["data"])
		df_hum = df_hum.rename(columns={"ts":"ts","value":"humidity"})
		df_hum = df_hum.set_index("ts")

		# merge dataframes
		df = pd.concat([df,df_hum],axis=1,join="inner")
	except Exception as e:
		print(f"{sensor_serial} - can't insert into dataframe: {e}")

	# insert dataframe into influxDB
	try:
		influxdb_connect.write_api.write(
			bucket=config.influx_bucket,
			org=config.influx_org,
			record=df,
			data_frame_measurement_name=sensor_name_mapping[sensor_serial])
		print(f"{sensor_serial} - data successfully inserted.")
	except Exception as e:
		print(f"{sensor_serial} - can't write to database: {e}")

def put_historical_data_into_influx_door_water(sensor_serial,sensor_type,timespan,resolution):
	"""
	Insert historical data into InfluxDB - door or waterleak
	Using the Meraki Dashboard API functions 
	"""
	# read temperature data + insert into dataframe
	try:
		temperature_readings = get_historical_sensor_reading(sensor_serial,sensor_type,timespan,resolution)
		time.sleep(5)
		df = pd.DataFrame(temperature_readings[0]["data"])
		df = df.rename(columns={"ts":"ts","value":"status"})
		df = df.set_index("ts")
	except Exception as e:
		print(f"{sensor_serial} - can't insert into dataframe: {e}")
	
	# insert dataframe into influxDB
	try:
		influxdb_connect.write_api.write(
			bucket=config.influx_bucket,
			org=config.influx_org,
			record=df,
			data_frame_measurement_name=sensor_name_mapping[sensor_serial])
		print(f"{sensor_serial} - data successfully inserted.")
	except Exception as e:
		print(f"{sensor_serial} - can't write to database: {e}")


def main():
	"""
	starts when main is started in a thread
	"""

	# Mapping sensor name with serials from config.py
	print("Getting Meraki sensor information from Meraki Dashboard API")
	global sensor_name_mapping
	sensor_name_mapping = get_sensor_name_mapping()

	# Gets at first the hisorical sensor data from the sensors in config.py
	print("Getting historical sensor data")
	for s in config.temperature_sensors:
		put_historical_data_into_influx_temp_hum(s,2592000,3600) #last 30 days, sensor reading every 60 min, average

	for s in config.door_sensors:
		put_historical_data_into_influx_door_water(s,"door",86400,120) #last day, sensor reading every 2 min

	for s in config.waterleak_sensors:
		put_historical_data_into_influx_door_water(s,"water_detection",86400,120) #last day, sensor reading every 2 min

	# Requests every 10min the latest sensor data from the Meraki Dashboard and inserts the data into influxDB
	while True:
		print("Polling now latest sensor data")
		for s in config.temperature_sensors:
			try:
				r = get_latest_sensor_reading(s,"temperature")
				r_hum = get_latest_sensor_reading(s,"humidity")
				r = r[0]
				r_hum = r_hum[0]
				influxdb_connect.write_api.write(
					bucket=config.influx_bucket,
					org=config.influx_org,
					record=influxdb_connect.Point(sensor_name_mapping[r["serial"]])
					.field("temperature",r["value"])
					.field("humidity",r_hum["value"])
					.time(r["ts"]))
			except Exception as e:
				print("Can't write to database: {}".format(e))
			
		for s in config.door_sensors:
			try:
				r = get_latest_sensor_reading(s,"door")
				r = r[0]
				influxdb_connect.write_api.write(
					bucket=config.influx_bucket,
					org=config.influx_org,
					record=influxdb_connect.Point(sensor_name_mapping[r["serial"]])
					.field("status",r["value"])
					.time(r["ts"]))
			except Exception as e:
				print("Can't write to database: {}".format(e))

		for s in config.waterleak_sensors:
			try:
				r = get_latest_sensor_reading(s,"water_detection")
				r = r[0]
				influxdb_connect.write_api.write(
					bucket=config.influx_bucket,
					org=config.influx_org,
					record=influxdb_connect.Point(sensor_name_mapping[r["serial"]])
					.field("status",r["value"])
					.time(r["ts"]))
			except Exception as e:
				print("Can't write to database: {}".format(e))
		
		time.sleep(600) #poll every 10minutes