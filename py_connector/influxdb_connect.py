# Asset Monitoring Dashboard 1.0
# Cisco Meraki IoT + Cisco Industrial Asset Vision
# MIT License, flopach / Cisco Systems 2021

from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import config
from urllib3 import Retry

#influxdb connect
retries = Retry(connect=10, read=5, redirect=10)
influx_client = InfluxDBClient(url=config.influx_url, token=config.influx_token, org=config.influx_org,retries=retries) #debug=True
write_api = influx_client.write_api(write_options=SYNCHRONOUS)