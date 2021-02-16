FROM python:3.7-slim

RUN pip install influxdb_client paho-mqtt requests pandas urllib3

COPY iav_to_influx.py /py_connector/
COPY meraki_to_influx.py /py_connector/
COPY config.py /py_connector/
COPY main.py /py_connector/
COPY influxdb_connect.py /py_connector/

CMD ["python", "-u", "/py_connector/main.py"]