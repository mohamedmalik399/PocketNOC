import subprocess
import os
import socket
import threading
import time
from datetime import datetime

from inventory import discover_devices

from database import (
    init_database,
    save_event,
    save_uptime,
    get_uptime,
    save_measurement,
    save_alert,
    save_snmp_interface_measurement
)
from snmp_interface_monitor import get_interface_data

network_data = []

lock = threading.Lock()

previous_states = {}

state_times = {}

uptime_data = {}

failure_counts = {}
success_counts = {}

ICMP_FAILURE_THRESHOLD = 3
ICMP_RECOVERY_THRESHOLD = 2

snmp_previous = {}

snmp_previous_time = {}

MONITORED_SERVICES = {
    os.getenv("POCKETNOC_MONITOR_HOST", "127.0.0.1"): [
        {
            "name": "SSH",
            "port": 8022
        }
    ]
}

def calculate_snmp_rate(key, rx_bytes, tx_bytes):
    now = time.time()

    previous = snmp_previous.get(key)
    previous_time = snmp_previous_time.get(key)

    snmp_previous[key] = {
        "rx": rx_bytes,
        "tx": tx_bytes
    }

    snmp_previous_time[key] = now

    if previous is None or previous_time is None:
        return {
            "rx_bps": 0,
            "tx_bps": 0
        }

    elapsed = now - previous_time

    if elapsed <= 0:
        return {
            "rx_bps": 0,
            "tx_bps": 0
        }

    rx_difference = rx_bytes - previous["rx"]
    tx_difference = tx_bytes - previous["tx"]

    if rx_difference < 0:
        rx_difference = 0

    if tx_difference < 0:
        tx_difference = 0

    rx_bps = (rx_difference * 8) / elapsed
    tx_bps = (tx_difference * 8) / elapsed

    return {
        "rx_bps": rx_bps,
        "tx_bps": tx_bps
    }

def ping_device(ip):

    result = subprocess.run(
        ["ping", "-c", "1", "-W", "2", ip],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    return result.returncode == 0


def check_tcp(ip, port):

    try:

        sock = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        )

        sock.settimeout(2)

        result = sock.connect_ex(
            (ip, port)
        )

        sock.close()

        return result == 0

    except Exception:

        return False

def check_dns():
    try:
        result = subprocess.run(
            [
                "dig",
                "@8.8.8.8",
                "google.com",
                "+time=2",
                "+tries=1",
                "+short"
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True
        )

        return bool(result.stdout.strip())

    except Exception:
        return False

def log_event(
         device,
         service,
         old_state,
         new_state
    ):

    timestamp = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )


    message = (
        f"{device} {service} "
        f"changed from "
        f"{old_state} to {new_state}"
    )


    with open(
        "logs/events.log",
        "a"
    ) as log:

        log.write(
            f"[{timestamp}] "
            f"{message}\n"
        )


    save_event(
        timestamp,
        device,
        service,
        old_state,
        new_state
    )


    print(
        f"[EVENT] "
        f"[{timestamp}] "
        f"{message}"
    )

    if new_state == "DOWN":
        with open("logs/alerts.log", "a") as alert_log:
            alert_log.write(
                f"[{timestamp}] ALERT: "
                f"{device} {service} is DOWN\n"
            )

        print(
            f"[ALERT] [{timestamp}] "
            f"{device} {service} is DOWN"
        )

    if new_state == "DOWN":
        message = f"{device} {service} is DOWN"

        save_alert(
            timestamp,
            device,
            service,
            "ACTIVE",
            message
        )

    elif new_state == "UP" and old_state == "DOWN":
        message = f"{device} {service} recovered"

        save_alert(
            timestamp,
            device,
            service,
            "RESOLVED",
            message
        )

def update_uptime(key, new_state):

    now = time.time()

    old_state = previous_states.get(key)

    # First observation
    if old_state is None:

        previous_states[key] = new_state

        now = time.time()

        state_times[key] = now

        uptime_data[key] = {
            "state": new_state,
            "up_seconds": 0,
            "down_seconds": 0,
            "last_change": datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
        )
    }

    return


    # No state change
    if old_state == new_state:

        elapsed = now - state_times[key]

        if old_state == "UP":

            uptime_data[key]["up_seconds"] += elapsed

        else:

            uptime_data[key]["down_seconds"] += elapsed

        state_times[key] = now

        return


    # State changed
    elapsed = now - state_times[key]

    if old_state == "UP":

        uptime_data[key]["up_seconds"] += elapsed

    else:

        uptime_data[key]["down_seconds"] += elapsed


    timestamp = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    uptime_data[key]["state"] = new_state

    uptime_data[key]["last_change"] = timestamp

    previous_states[key] = new_state

    state_times[key] = now


def check_for_change(key, new_state):
    old_state = previous_states.get(key)

    # First observation
    if old_state is None:
        previous_states[key] = new_state

        if new_state == "UP":
            update_uptime(key, "UP")
        else:
            update_uptime(key, "DOWN")

        return

    # ICMP debounce
    if key.endswith(" ICMP"):

        if new_state == "DOWN":
            failure_counts[key] = failure_counts.get(key, 0) + 1
            success_counts[key] = 0

            if (
                old_state == "UP"
                and failure_counts[key] >= ICMP_FAILURE_THRESHOLD
            ):
                previous_states[key] = "DOWN"
                update_uptime(key, "DOWN")

                parts = key.split(" ", 1)
                device = parts[0]
                service = parts[1]

                log_event(
                    device,
                    service,
                    "UP",
                    "DOWN"
                )

        elif new_state == "UP":
            success_counts[key] = success_counts.get(key, 0) + 1
            failure_counts[key] = 0

            if (
                old_state == "DOWN"
                and success_counts[key] >= ICMP_RECOVERY_THRESHOLD
            ):
                previous_states[key] = "UP"
                update_uptime(key, "UP")

                parts = key.split(" ", 1)
                device = parts[0]
                service = parts[1]

                log_event(
                    device,
                    service,
                    "DOWN",
                    "UP"
                )

        return

    # Existing behavior for TCP/DNS/etc.
    update_uptime(key, new_state)

    if old_state != new_state:
        previous_states[key] = new_state

        parts = key.split(" ", 1)
        device = parts[0]
        service = parts[1]

        log_event(
            device,
            service,
            old_state,
            new_state
        )

def monitor_network():

    global network_data

    while True:

        print(
            "\n[POCKETNOC] Starting discovery..."
        )


        discovered = discover_devices()

        results = []


        dns_up = check_dns()
        dns_state = "UP" if dns_up else "DOWN"

        check_for_change(
            "8.8.8.8 DNS",
            dns_state
        )

        save_measurement(
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "8.8.8.8",
            "DNS",
            dns_state
        )

        try:
            snmp_interfaces = get_interface_data()
        except Exception as e:
            print(f"[SNMP] Error: {e}")
            snmp_interfaces = []

        for interface in snmp_interfaces:

            key = interface["name"]

            rates = calculate_snmp_rate(
                key,
                interface["rx_bytes"],
                interface["tx_bytes"]
            )

            interface["rx_bps"] = rates["rx_bps"]
            interface["tx_bps"] = rates["tx_bps"]

            save_snmp_interface_measurement(
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                interface["index"],
                interface["name"],
                interface["status"],
                interface["rx_bytes"],
                interface["tx_bytes"],
                interface["rx_bps"],
                interface["tx_bps"]
            )

            print(
                f"[SNMP] "
                f"{interface['name']} "
                f"{interface['status']} "
                f"RX={interface['rx_bytes']} "
                f"TX={interface['tx_bytes']} "
                f"RX_RATE={interface['rx_bps']:.2f} bps "
                f"TX_RATE={interface['tx_bps']:.2f} bps"
            )

        for device in discovered:

            ip = device["ip"]

            print(
                f"[MONITOR] Checking {ip}"
            )


            # ICMP

            icmp_up = ping_device(ip)

            icmp_state = (
                "UP"
                if icmp_up
                else "DOWN"
            )

            save_measurement(
 	        datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
            ),
            ip,
            "ICMP",
            icmp_state
            )


            check_for_change(
                f"{ip} ICMP",
                icmp_state
            )


            tcp_services = {}

            services = MONITORED_SERVICES.get(ip, [])

            for service in services:

                service_name = service["name"]
                port = service["port"]

                tcp_up = check_tcp(ip, port)
                tcp_state = "UP" if tcp_up else "DOWN"

                key = f"{ip} TCP {port}"

                check_for_change(
                    key,
                    tcp_state
                )

                save_measurement(
                    datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),
                    ip,
                    f"TCP {port}",
                    tcp_state
                )

                tcp_services[service_name] = {
                    "port": port,
                    "state": tcp_state
                }


            results.append({

                "ip": ip,

                "mac": device["mac"],

                "vendor": device["vendor"],

                "icmp": icmp_state,

                "tcp_services": tcp_services

            })


        with lock:

            network_data = results



        for key, stats in uptime_data.items():

         parts = key.split(" ", 1)

         device = parts[0]

         service = parts[1]

         save_uptime(
         	device,
         	service,
         	stats["state"],
         	stats["up_seconds"],
         	stats["down_seconds"],
         	stats["last_change"]
         )


        print(
            f"[POCKETNOC] "
            f"{len(results)} devices monitored"
        )


        time.sleep(30)


def get_network_data():

    with lock:

        return list(network_data)


def get_uptime_data():

    with lock:

        return dict(uptime_data)

init_database()

for record in get_uptime():

    key = (
        f"{record['device']} "
        f"{record['service']}"
    )

    previous_states[key] = record["state"]

    uptime_data[key] = {
        "state": record["state"],
        "up_seconds": record["up_seconds"],
        "down_seconds": record["down_seconds"],
        "last_change": record["last_change"]
    }

    state_times[key] = time.time()

thread = threading.Thread(
    target=monitor_network,
    daemon=True
)

thread.start()
