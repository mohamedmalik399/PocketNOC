import subprocess
import os
import re
import socket
import time
from datetime import datetime

NETWORK = os.getenv("POCKETNOC_NETWORK", "192.0.2.0/24")
LOG_FILE = "logs/auto_network_monitor.log"


def discover_devices():
    result = subprocess.run(
        ["nmap", "-sn", NETWORK],
        capture_output=True,
        text=True
    )

    ips = re.findall(
        r"Nmap scan report for (\d+\.\d+\.\d+\.\d+)",
        result.stdout
    )

    return ips


def ping_device(ip):
    result = subprocess.run(
        ["ping", "-c", "1", "-W", "2", ip],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    return result.returncode == 0


def check_port(ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)

    try:
        return sock.connect_ex((ip, port)) == 0
    except Exception:
        return False
    finally:
        sock.close()


while True:

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print("\n" + "=" * 70)
    print("POCKETNOC AUTOMATIC NETWORK MONITOR")
    print(timestamp)
    print("=" * 70)

    devices = discover_devices()

    print(f"\nDiscovered {len(devices)} active devices\n")

    with open(LOG_FILE, "a") as log:

        log.write(
            f"\n[{timestamp}] Discovery scan\n"
        )

        for ip in devices:

            icmp_status = "UP" if ping_device(ip) else "DOWN"

            print(
                f"{ip:15} ICMP: {icmp_status}"
            )

            log.write(
                f"{timestamp} | {ip} | ICMP | {icmp_status}\n"
            )

            # Check SSH on the P9 Lite
            if ip == os.getenv("POCKETNOC_MONITOR_HOST", "127.0.0.1"):

                ssh_status = (
                    "UP"
                    if check_port(ip, 8022)
                    else "DOWN"
                )

                print(
                    f"{'':15} TCP/8022: {ssh_status}"
                )

                log.write(
                    f"{timestamp} | {ip} | TCP/8022 | {ssh_status}\n"
                )

    print("\nNext discovery in 60 seconds...")

    time.sleep(60)
