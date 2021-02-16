# Asset Monitoring Dashboard

2in1 Dashboard for Cisco Meraki IoT Sensors + Cisco Industrial Asset Vision Sensors. Simply install your own dashboard anywhere within minutes.

![](images/grafana-dashboard.png)

![](images/architecture.png)

## Installation

**Prerequisites**:

* git, Docker/Docker-compose installed
* For Cisco Industrial Asset Vision (IAV): MQTT broker is setup or this environment is open for MQTT connectivity.

1. Clone repository `git clone https://github.com/flopach/asset-monitoring-dashboard`

2. Configure your environment and insert your data into the `py_connector/config.py` file.


3. Start all containers with `docker-compose up` from the same directory. This may take several minutes.

4. Login to Grafana dashboard and configure the dashboard by easily inserting the measurement. Additionally the query editor from the InfluxDB UI can help.

Login **Grafana** - [http://localhost:3000](http://localhost:3000)

* username: admin
* password: admin123

![](images/grafana-query.png)

Login **InfluxDB** - [http://localhost:8086](http://localhost:3000)

* username: admin
* password: admin123

![](images/influxdb-query.png)

## Features

* Data will remain in the project folder even after the containers are shut down
* All Meraki sensor types are support.
* All IAV sensor types are supported except the GPS sensors.

## Versioning

**1.0** (Feb 2021) - Initial version.


## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Further Links

* [Cisco DevNet Website](https://developer.cisco.com)