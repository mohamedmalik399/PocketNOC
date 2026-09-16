# PocketNOC

A lightweight Network Operations Center (NOC) monitoring system built with **Python, Flask, SQLite, SNMP, Syslog, and network discovery tools**.

PocketNOC was created as a practical networking project for learning how real network-monitoring systems work — from device discovery and connectivity checks to service monitoring, SNMP statistics, traffic monitoring, event logging, alerts, and a web-based NOC dashboard.

---

## 1. Overview

PocketNOC is a small network monitoring platform designed to run on a low-resource device such as an Android phone running Termux.

It continuously monitors network devices and services and presents collected information through a web dashboard and API.

The project combines networking concepts with Python programming, Linux/Termux, network-management protocols, databases, and web development.

### Main technologies

* Python
* Flask
* SQLite
* Nmap
* SNMP
* Syslog
* TCP
* ICMP
* DNS
* HTML/CSS/JavaScript
* Termux
* Git/GitHub

---

## 2. Main Features

PocketNOC currently provides:

* Automatic network discovery
* ICMP monitoring
* TCP service monitoring
* DNS availability monitoring
* SNMP system monitoring
* SNMP interface monitoring
* RX/TX traffic monitoring
* Historical SNMP traffic data
* Syslog collection
* Event history
* Alert management
* Device uptime tracking
* SQLite persistence
* REST-style API
* Flask web dashboard
* HTTP Basic Authentication
* Environment-based configuration

---

## 3. Architecture

```text
                    Network
                       |
        +--------------+--------------+
        |              |              |
       ICMP           TCP            SNMP
        |              |              |
        +--------------+--------------+
                       |
                       v
              +----------------+
              |   PocketNOC    |
              | Android/Termux |
              +----------------+
                       |
        +--------------+--------------+
        |              |              |
   Monitoring       SQLite         Syslog
     Engine        Database        Receiver
        |              |              |
        +--------------+--------------+
                       |
                       v
                Flask REST API
                       |
                       v
                Web Dashboard
```

The project follows an API-first design:

```text
Monitoring
    |
    v
Database
    |
    v
API
    |
    v
Dashboard
```

---

## 4. Project Structure

```text
PocketNOC/
├── dashboard.py
├── network_engine.py
├── database.py
├── inventory.py
├── discover.py
├── device_inventory.py
├── auto_network_monitor.py
├── snmp_monitor.py
├── snmp_interfaces.py
├── snmp_interface_monitor.py
├── snmp_traffic.py
├── syslog_server.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

Runtime and private files are intentionally excluded from Git.

Examples include:

```text
.env
pocketnoc.db
logs/
__pycache__/
*.pyc
snmpd.conf
snmpd.pid
```

---

## 5. File Responsibilities

### dashboard.py

Runs the Flask application and provides:

* Web dashboard
* API endpoints
* Authentication
* Monitoring views
* SNMP information
* Traffic history

### network_engine.py

Provides network monitoring functionality including:

* ICMP checks
* TCP service checks
* DNS checks
* State tracking
* Events
* Alerts

### database.py

Handles SQLite database operations and persistence.

### discover.py

Performs network discovery using Nmap.

### inventory.py

Handles network device inventory information.

### device_inventory.py

Processes discovered devices and inventory data.

### auto_network_monitor.py

Provides automatic monitoring using the configured network range.

### snmp_monitor.py

Collects SNMP system information.

### snmp_interfaces.py

Discovers SNMP interfaces and their counters/status.

### snmp_interface_monitor.py

Monitors SNMP interface state and counters.

### snmp_traffic.py

Calculates RX/TX traffic rates from SNMP counters.

### syslog_server.py

Receives and processes UDP syslog messages.

---

## 6. Requirements

PocketNOC requires:

* Python 3
* Flask
* Termux or a Linux-like environment
* Nmap
* Net-SNMP tools for SNMP functionality

Install Python dependencies:

```bash
pip install -r requirements.txt
```

---

## 7. Installation

Clone the repository:

```bash
git clone https://github.com/mohamedmalik399/PocketNOC.git
```

Enter the project:

```bash
cd PocketNOC
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## 8. Configuration

PocketNOC uses environment variables instead of hard-coded credentials and private network information.

Example:

```bash
export POCKETNOC_USER=admin
export POCKETNOC_PASSWORD='change-me'
export POCKETNOC_NETWORK='192.0.2.0/24'
export POCKETNOC_MONITOR_HOST='127.0.0.1'
export POCKETNOC_SNMP_TARGET='127.0.0.1:1161'
export POCKETNOC_SNMP_COMMUNITY='change-me'
```

The example values are placeholders.

Use your real network values only in your local environment.

---

## 9. Environment Variables

### POCKETNOC_USER

Dashboard username.

### POCKETNOC_PASSWORD

Dashboard password.

### POCKETNOC_NETWORK

Network range used for discovery and automatic monitoring.

Example:

```text
192.0.2.0/24
```

### POCKETNOC_MONITOR_HOST

Host used for local service monitoring.

### POCKETNOC_SNMP_TARGET

SNMP target in:

```text
host:port
```

format.

### POCKETNOC_SNMP_COMMUNITY

SNMP community string.

Never publish a real SNMP community string.

---

## 10. Running PocketNOC

After configuration:

```bash
python dashboard.py
```

The Flask application starts the web dashboard and API.

The exact listening address and port depend on the application configuration.

---

## 11. Dashboard Authentication

PocketNOC supports HTTP Basic Authentication.

Credentials are loaded from environment variables.

This avoids putting a real password directly into Python source code.

For real deployments:

* Use a strong password
* Never commit credentials
* Restrict access to trusted networks
* Prefer HTTPS for sensitive deployments
* Do not expose the dashboard directly to the public Internet without appropriate security controls

---

## 12. Network Discovery

Nmap is used to discover devices in the configured network.

The general workflow is:

```text
Network Range
     |
     v
    Nmap
     |
     v
Discovered Hosts
     |
     v
Inventory
     |
     v
Monitoring
```

Network discovery allows PocketNOC to identify devices that may need monitoring.

---

## 13. ICMP Monitoring

ICMP monitoring checks whether a device is reachable.

Basic workflow:

```text
PocketNOC
    |
    | ICMP Echo
    v
Network Device
    |
    +---- Reply = UP
    |
    +---- Timeout = DOWN
```

ICMP monitoring is useful for determining basic IP reachability.

It does not prove that every service on the device is working.

---

## 14. TCP Service Monitoring

PocketNOC can check TCP service ports.

Example:

```text
PocketNOC
    |
    | TCP connection
    v
Device:Port
    |
    +---- Connection succeeds = UP
    |
    +---- Connection fails = DOWN
```

TCP monitoring checks whether a service port is reachable.

It does not necessarily prove that the application itself is functioning correctly.

---

## 15. DNS Monitoring

DNS monitoring checks DNS availability.

It helps distinguish between:

```text
Internet/network connectivity
```

and:

```text
DNS resolution problems
```

This is useful during network troubleshooting.

---

## 16. SNMP Monitoring

SNMP allows PocketNOC to collect management information from compatible devices.

PocketNOC can monitor:

* System description
* System uptime
* Interface names
* Interface status
* Interface counters
* RX traffic
* TX traffic

The project demonstrates the basic relationship:

```text
SNMP Manager
     |
     | SNMP Request
     v
SNMP Agent
     |
     | Response
     v
SNMP Manager
```

---

## 17. SNMP Interface Monitoring

Network interfaces expose information through SNMP.

PocketNOC can monitor:

* Interface name
* Interface status
* Interface counters
* Incoming bytes
* Outgoing bytes

This provides visibility into interface activity.

---

## 18. SNMP Traffic Monitoring

SNMP traffic monitoring uses interface byte counters.

A traffic rate can be calculated using the change in counters over time:

```text
rate = counter difference / time difference
```

The monitoring process is:

```text
Read counter
     |
     v
Wait
     |
     v
Read counter again
     |
     v
Calculate difference
     |
     v
Calculate traffic rate
```

Historical values can then be stored and displayed as graphs.

---

## 19. Syslog

PocketNOC includes a UDP syslog receiver.

Basic workflow:

```text
Network Device
      |
      | UDP Syslog
      v
Syslog Receiver
      |
      v
Event Storage
      |
      v
Dashboard / API
```

Syslog allows network devices and services to send operational messages to PocketNOC.

---

## 20. Events

PocketNOC records important monitoring events.

Examples:

* Device became unreachable
* Device recovered
* TCP service failed
* TCP service recovered
* DNS check failed
* DNS check recovered
* Syslog message received

Events provide historical information for troubleshooting.

---

## 21. Alerts

Alerts represent conditions that require attention.

A typical lifecycle is:

```text
OK
 |
 | Failure
 v
ALERT
 |
 | Recovery
 v
RECOVERED
```

This helps distinguish a continuing failure from a recovered failure.

---

## 22. Uptime Monitoring

PocketNOC tracks device/service availability over time.

Example:

```text
Check
 |
 +---- UP   -> successful measurement
 |
 +---- DOWN -> failure measurement
```

Historical uptime information can be used to understand availability.

---

## 23. Historical Monitoring

PocketNOC stores monitoring information in SQLite.

Historical data can be used for:

* Availability graphs
* Traffic graphs
* Event history
* Alert history
* Troubleshooting

SQLite allows data to remain available after application restarts.

---

## 24. Database

PocketNOC uses SQLite for local persistence.

The database can contain information related to:

* Events
* Measurements
* Uptime
* Alerts
* Historical monitoring data

The database file is runtime data and is intentionally excluded from Git.

---

## 25. REST API

PocketNOC exposes monitoring information through Flask API endpoints.

The architecture separates data collection from presentation:

```text
Monitoring Engine
       |
       v
SQLite
       |
       v
Flask API
       |
       v
Web Dashboard
```

This makes it possible to create additional clients in the future.

---

## 26. Web Dashboard

The dashboard provides a NOC-style interface for monitoring the system.

It can display information such as:

* Device availability
* TCP services
* DNS status
* SNMP information
* Interface status
* Traffic history
* Events
* Alerts
* Uptime

The dashboard consumes data from the Flask application.

---

## 27. Troubleshooting Model

A useful troubleshooting order is:

```text
1. Physical / Wi-Fi connectivity
2. IP addressing
3. ARP / neighbor resolution
4. ICMP reachability
5. TCP port reachability
6. DNS
7. Application/service
8. SNMP
9. Syslog
10. Dashboard/API
```

This follows a layered troubleshooting approach commonly used in networking.

---

## 28. CCNA Learning Value

PocketNOC provides practical examples of CCNA concepts.

### IPv4

* IP addresses
* Subnets
* Network ranges
* Default gateways

### Ethernet

* MAC addresses
* Local network communication

### ICMP

* Reachability testing
* Failure detection

### TCP

* Ports
* Connections
* Service availability

### DNS

* Name resolution
* Troubleshooting

### Network Management

* SNMP
* Syslog
* Monitoring
* Events
* Alerts

### Automation

* Python
* APIs
* SQLite
* Web dashboards

---

## 29. Failure and Recovery Testing

Monitoring should be tested using both failure and recovery.

Example:

```text
Service UP
    |
    | Stop service
    v
Service DOWN
    |
    | Start service
    v
Service UP
```

Verify that:

1. Failure is detected.
2. An event is recorded.
3. An alert is created when configured.
4. Recovery is detected.
5. A recovery event is recorded.
6. The alert lifecycle changes appropriately.

---

## 30. Security

PocketNOC is an educational project and should be secured before production use.

Important rules:

* Never commit passwords
* Never commit real SNMP community strings
* Never commit `.env`
* Do not expose private network information unnecessarily
* Use strong credentials
* Restrict management access
* Prefer HTTPS for sensitive deployments
* Keep dependencies updated
* Do not expose SNMP to untrusted networks

---

## 31. Git Safety

The repository intentionally ignores runtime and private files.

The `.gitignore` includes:

```text
.env
pocketnoc.db
logs/
__pycache__/
*.pyc
snmpd.pid
snmpd.conf
snmpd.conf.save
```

Before committing:

```bash
git status
```

Review tracked files:

```bash
git ls-files
```

Review changes:

```bash
git diff
```

Never commit passwords, tokens, SNMP community strings, or other credentials.

---

## 32. Environment Example

The repository includes `.env.example`.

Example:

```env
POCKETNOC_USER=admin
POCKETNOC_PASSWORD=change-me
POCKETNOC_NETWORK=192.0.2.0/24
POCKETNOC_MONITOR_HOST=127.0.0.1
POCKETNOC_SNMP_TARGET=127.0.0.1:1161
POCKETNOC_SNMP_COMMUNITY=change-me
```

These are example values only.

---

## 33. Python Syntax Testing

Run:

```bash
python -m py_compile dashboard.py network_engine.py database.py inventory.py discover.py device_inventory.py auto_network_monitor.py snmp_monitor.py snmp_traffic.py snmp_interfaces.py snmp_interface_monitor.py
```

If the command produces no output, the Python files passed the syntax check.

---

## 34. Git Workflow

A normal development workflow is:

```text
Change code
    |
    v
Run syntax checks
    |
    v
Run application
    |
    v
Test feature
    |
    v
Review git diff
    |
    v
Commit
    |
    v
Push
```

Useful commands:

```bash
git status
git diff
git add .
git commit -m "Describe the change"
git push
```

---

## 35. Practical Monitoring Flow

A typical PocketNOC monitoring cycle is:

```text
Discover
   |
   v
Identify Devices
   |
   v
Check Reachability
   |
   v
Check Services
   |
   v
Collect SNMP Data
   |
   v
Receive Syslog
   |
   v
Store Data
   |
   v
Generate Events / Alerts
   |
   v
Expose API
   |
   v
Display Dashboard
```

---

## 36. Project Philosophy

PocketNOC is designed primarily as a learning and practical networking project.

The goal is to understand how a monitoring platform works rather than simply creating a dashboard.

The project separates:

* Discovery
* Monitoring
* Data collection
* Storage
* Events
* Alerts
* API
* Dashboard

This separation makes the system easier to understand, test, and extend.

---

## 37. Current Capabilities

PocketNOC currently demonstrates:

* Network discovery
* ICMP monitoring
* TCP service monitoring
* DNS monitoring
* SNMP system monitoring
* SNMP interface monitoring
* RX/TX traffic monitoring
* Historical traffic data
* Syslog collection
* SQLite persistence
* Events
* Alerts
* Uptime tracking
* Flask dashboard
* API access
* Authentication
* Environment-based configuration
* Git/GitHub repository management

---

## 38. Future Improvements

Possible future improvements include:

* HTTPS
* Role-based authentication
* Better device inventory
* Configurable monitoring intervals
* Additional SNMP metrics
* SNMPv3
* Email notifications
* Telegram notifications
* Configurable alert rules
* Dashboard filtering
* Device groups
* Exportable reports
* More detailed graphs
* Automatic service discovery
* Background task scheduling
* Containerized deployment
* High-availability monitoring

---

## 39. Limitations

PocketNOC is intentionally lightweight.

It is not intended to replace mature enterprise monitoring systems.

Possible limitations include:

* SQLite scalability
* Limited distributed monitoring
* Basic authentication
* Limited notification systems
* Dependence on local network visibility
* Limited SNMP device compatibility
* No built-in high-availability architecture

These limitations also provide opportunities for future development.

---

## 40. Educational Purpose

PocketNOC connects networking knowledge with practical software development.

```text
CCNA Networking
       +
Linux / Termux
       +
Python
       +
SNMP / Syslog
       +
SQLite
       +
Flask / API
       +
Web Dashboard
       =
Practical NOC Project
```

The project can therefore be used as a personal networking laboratory.

---

## 41. Repository

GitHub repository:

```text
https://github.com/mohamedmalik399/PocketNOC
```

---

## 42. Author

Mohamed Malik

PocketNOC is a personal networking, monitoring, and automation learning project.

---

## 43. License

Choose an appropriate open-source license before distributing the project publicly.

Possible choices include:

* MIT
* Apache-2.0
* GPL

The license should match the intended use and distribution requirements of the project.

---

## 44. Final Summary

PocketNOC demonstrates how a small device can be turned into a practical network-monitoring platform.

It combines:

* Network discovery
* ICMP
* TCP
* DNS
* SNMP
* Syslog
* SQLite
* Flask
* REST-style APIs
* Historical monitoring
* Events
* Alerts
* Authentication
* Git/GitHub

The main goal is not simply to display a dashboard.

The goal is to understand how network monitoring works from:

```text
Network
   |
   v
Data Collection
   |
   v
Monitoring
   |
   v
Database
   |
   v
API
   |
   v
Dashboard
```

PocketNOC is a practical networking project for learning, testing, experimenting, and building.

---

**PocketNOC — a practical networking project for learning, testing, and building.**

