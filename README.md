# PocketNOC

PocketNOC is a lightweight network monitoring and NOC dashboard built to run on an Android phone using Termux.

It provides network discovery, ICMP monitoring, TCP service checks, DNS monitoring, SNMP monitoring, syslog collection, event history, uptime tracking, alerts, SQLite persistence, a REST-style API, and a Flask web dashboard.

## Features

* Automatic network discovery with Nmap
* ICMP device monitoring
* TCP service monitoring
* DNS availability monitoring
* SNMP system information
* SNMP interface monitoring
* RX/TX traffic monitoring
* Historical SNMP traffic data
* Syslog receiver
* Event and alert history
* Device uptime tracking
* SQLite database persistence
* REST-style API endpoints
* Flask web dashboard
* HTTP Basic Authentication
* Failure and recovery detection
* Lightweight operation on Android/Termux

## Architecture

```text
                    Network Devices
                          |
              ICMP / TCP / SNMP / Syslog
                          |
                          v
              +-----------------------+
              |       PocketNOC       |
              |    Android + Termux   |
              +-----------------------+
                          |
          +---------------+---------------+
          |               |               |
          v               v               v
    Nmap Discovery   Network Engine   SNMP Monitoring
          |               |               |
          +---------------+---------------+
                          |
                          v
                  SQLite Database
                          |
          +---------------+---------------+
          |                               |
          v                               v
     REST API                       Flask Dashboard
                                          |
                                      Port 8080
```

## How It Works

PocketNOC runs on an Android phone using Termux.

The monitoring engine discovers devices on the configured network and checks their availability using ICMP and configured TCP services.

SNMP monitoring collects system and interface information from an SNMP-enabled device.

Syslog messages can be received and stored for later inspection.

Monitoring results and events are stored locally in SQLite.

The Flask dashboard reads the monitoring data through API endpoints and presents the information through a NOC-style web interface.

## Requirements

### Hardware

* Android phone
* Wi-Fi network
* Sufficient storage for Termux and monitoring data

### Software

* Termux
* Python 3
* Flask
* Nmap
* Net-SNMP tools
* Git

Python dependencies are listed in:

```text
requirements.txt
```

Install them with:

```bash
pip install -r requirements.txt
```

## Installation

Clone the repository:

```bash
git clone <repository-url>
cd PocketNOC
```

Install Python dependencies:

```bash
pip install -r requirements.txt
```

Make sure Nmap and the required Net-SNMP tools are installed in your environment.

## Configuration

PocketNOC uses environment variables for sensitive and environment-specific configuration.

The repository includes:

```text
.env.example
```

Create your local configuration:

```bash
cp .env.example .env
```

The application currently reads configuration from environment variables.

Example:

```bash
export POCKETNOC_USER=admin
export POCKETNOC_PASSWORD=your-password
export POCKETNOC_NETWORK=192.168.1.0/24
export POCKETNOC_MONITOR_HOST=127.0.0.1
export POCKETNOC_SNMP_TARGET=127.0.0.1:1161
export POCKETNOC_SNMP_COMMUNITY=your-community
```

### Configuration Variables

| Variable                   | Purpose                         |
| -------------------------- | ------------------------------- |
| `POCKETNOC_USER`           | Dashboard username              |
| `POCKETNOC_PASSWORD`       | Dashboard password              |
| `POCKETNOC_NETWORK`        | Network/CIDR used for discovery |
| `POCKETNOC_MONITOR_HOST`   | Host used for TCP monitoring    |
| `POCKETNOC_SNMP_TARGET`    | SNMP target address and port    |
| `POCKETNOC_SNMP_COMMUNITY` | SNMP community string           |

Do not commit real credentials or private configuration to GitHub.

## Running PocketNOC

### 1. Configure the environment

Example:

```bash
export POCKETNOC_USER=admin
export POCKETNOC_PASSWORD=your-password
export POCKETNOC_NETWORK=192.168.1.0/24
export POCKETNOC_MONITOR_HOST=127.0.0.1
export POCKETNOC_SNMP_TARGET=127.0.0.1:1161
export POCKETNOC_SNMP_COMMUNITY=your-community
```

### 2. Start the monitoring engine

```bash
python network_engine.py
```

The network engine performs monitoring and stores results in SQLite.

### 3. Start the Flask dashboard

In another Termux session:

```bash
python dashboard.py
```

The dashboard listens on port `8080`.

Open:

```text
http://<phone-ip>:8080
```

For example, if the phone's current LAN address is `192.168.x.x`:

```text
http://192.168.x.x:8080
```

Use the username and password configured through the environment variables.

## Monitoring

### Network Discovery

PocketNOC uses Nmap host discovery to identify active devices on the configured network.

The network is controlled by:

```text
POCKETNOC_NETWORK
```

Example:

```bash
export POCKETNOC_NETWORK=192.168.1.0/24
```

The public example configuration uses a documentation network instead of a real private LAN.

### ICMP Monitoring

Devices discovered on the network can be monitored using ICMP ping.

PocketNOC records device state changes and uses failure/recovery thresholds to reduce false alerts caused by temporary packet loss.

### TCP Monitoring

Specific TCP services can be monitored by IP address and port.

For example:

```text
SSH
TCP port 8022
```

The monitored host is configurable through:

```text
POCKETNOC_MONITOR_HOST
```

### DNS Monitoring

PocketNOC can perform DNS availability checks to verify that DNS resolution is working.

### SNMP Monitoring

PocketNOC uses Net-SNMP to collect information from an SNMP-enabled target.

The SNMP target is configured using:

```text
POCKETNOC_SNMP_TARGET
```

The SNMP community is configured using:

```text
POCKETNOC_SNMP_COMMUNITY
```

SNMP monitoring can collect:

* System description
* System uptime
* System location
* System contact
* Interface names
* Interface operational status
* RX counters
* TX counters
* RX traffic rate
* TX traffic rate

### SNMP Traffic

PocketNOC calculates traffic rates from SNMP interface counters.

The dashboard can display historical traffic measurements for monitored interfaces.

Typical interface information includes:

```text
Interface
Status
RX
TX
RX Rate
TX Rate
```

### Syslog

PocketNOC includes a UDP syslog receiver for collecting network device log messages.

Syslog messages can be parsed and stored in the SQLite database.

The dashboard exposes syslog information through an API endpoint.

## Database

PocketNOC uses SQLite for local persistence.

The database contains monitoring information such as:

* Events
* Uptime
* Measurements
* Alerts
* SNMP interface measurements
* Syslog events

The database file is:

```text
pocketnoc.db
```

The database is intentionally excluded from Git using `.gitignore`.

This prevents personal monitoring history and local network data from being published.

## API

PocketNOC exposes monitoring information through Flask API endpoints.

Important endpoints include:

```text
/api/devices
/api/inventory
/api/uptime
/api/measurements
/api/availability
/api/syslog
/api/snmp
/api/snmp/interfaces
```

The web dashboard consumes these endpoints to display monitoring information.

## Dashboard

The dashboard provides a NOC-style monitoring interface.

It can display information such as:

* Network devices
* Device availability
* ICMP status
* TCP service status
* Uptime
* Events
* Alerts
* Syslog messages
* SNMP system information
* SNMP interfaces
* RX/TX traffic
* Historical measurements

The dashboard uses HTTP Basic Authentication.

Authentication credentials are supplied through environment variables and are not stored directly in the source code.

## Alerts

PocketNOC records monitoring failures and recovery events.

The monitoring engine can detect:

* Device going down
* Device recovering
* TCP service failure
* TCP service recovery
* Other monitoring state changes

Alert information is stored locally in SQLite.

## Failure and Recovery Detection

PocketNOC uses thresholds for ICMP failure and recovery detection.

Example configuration:

```text
ICMP_FAILURE_THRESHOLD = 3
ICMP_RECOVERY_THRESHOLD = 2
```

This means a temporary single failed ping does not immediately have to produce a device-down state.

Repeated failures can trigger the failure state, while successful checks are required for recovery.

This helps reduce false alerts caused by transient packet loss.

## Project Structure

```text
PocketNOC/
│
├── dashboard.py
├── network_engine.py
├── database.py
│
├── inventory.py
├── discover.py
├── device_inventory.py
├── auto_network_monitor.py
│
├── snmp_monitor.py
├── snmp_interfaces.py
├── snmp_interface_monitor.py
├── snmp_traffic.py
│
├── syslog_server.py
│
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

Runtime files are intentionally not included in the repository:

```text
pocketnoc.db
logs/
__pycache__/
.env
snmpd.conf
snmpd.conf.save
snmpd.pid
```

## Testing

Check Python syntax:

```bash
python -m py_compile \
dashboard.py \
network_engine.py \
database.py \
inventory.py \
discover.py \
device_inventory.py \
auto_network_monitor.py \
snmp_monitor.py \
snmp_traffic.py \
snmp_interfaces.py \
snmp_interface_monitor.py
```

If the command returns no output, the files passed the Python compilation check.

## Troubleshooting

### Dashboard does not open

Check that Flask is running:

```bash
ps -ef | grep dashboard.py
```

Check that port 8080 is listening:

```bash
ss -lnt | grep 8080
```

Check the phone's current IP:

```bash
ip addr show wlan0
```

Then open:

```text
http://<phone-ip>:8080
```

### SNMP is not working

Check the SNMP process:

```bash
ps -ef | grep snmpd
```

Check the listening port:

```bash
ss -lun | grep 1161
```

Verify the environment variables:

```bash
echo $POCKETNOC_SNMP_TARGET
echo $POCKETNOC_SNMP_COMMUNITY
```

Do not publish the community string.

### Network discovery does not find devices

Check the configured network:

```bash
echo $POCKETNOC_NETWORK
```

Test Nmap manually:

```bash
nmap -sn "$POCKETNOC_NETWORK"
```

Make sure the phone is connected to the expected Wi-Fi network.

## Security

PocketNOC is designed primarily as an educational and laboratory monitoring project.

Never commit:

* Passwords
* SNMP community strings
* `.env`
* `snmpd.conf`
* `snmpd.conf.save`
* SQLite databases
* Monitoring logs
* Runtime PID files
* Private network information

Use strong credentials for dashboard authentication.

Restrict access to the dashboard and SNMP services to trusted networks.

Do not expose the Flask development server or SNMP service directly to the public Internet without appropriate security controls.

## Educational Goals

PocketNOC was built as a practical networking project to connect CCNA concepts with real-world network monitoring.

The project demonstrates practical concepts including:

* IPv4 networking
* Subnetting
* ICMP
* TCP
* DNS
* Network discovery
* SNMP
* Syslog
* Network monitoring
* Event logging
* Alerting
* Uptime monitoring
* REST APIs
* SQLite
* Flask
* HTTP authentication
* Linux/Android networking
* Troubleshooting

## Learning Outcomes

The project provides practical experience with the relationship between:

```text
Network
   ↓
Discovery
   ↓
Monitoring
   ↓
Data Collection
   ↓
Database
   ↓
API
   ↓
Dashboard
   ↓
Alerts
```

This architecture demonstrates how a basic network monitoring system can be built from individual networking concepts.

## Future Improvements

Possible future improvements include:

* SNMP trap support
* More protocol checks
* Configurable monitoring rules
* User management
* Role-based authentication
* More dashboard visualizations
* Notification integrations
* Configuration through the web interface
* Improved service discovery
* Containerized deployment
* HTTPS support
* More advanced alerting
* Network topology visualization

## Disclaimer

PocketNOC is an educational and experimental network monitoring project.

Only monitor networks, systems, and devices that you own or have explicit permission to monitor.

The project should be adapted and secured appropriately before being used in a production environment.
