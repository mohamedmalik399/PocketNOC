import subprocess
import os
import re


def discover_devices():

    result = subprocess.run(
        [
            "nmap",
            "-sn",
            os.getenv("POCKETNOC_NETWORK", "192.0.2.0/24")
        ],
        capture_output=True,
        text=True
    )

    output = result.stdout

    devices = []

    current_ip = None
    current_mac = None
    current_vendor = "Unknown"

    for line in output.splitlines():

        ip_match = re.search(
            r"Nmap scan report for .*?\((192\.168\.1\.\d+)\)",
            line
        )

        if not ip_match:
            ip_match = re.search(
                r"Nmap scan report for (192\.168\.1\.\d+)",
                line
            )

        if ip_match:

            if current_ip:

                devices.append({
                    "ip": current_ip,
                    "mac": current_mac,
                    "vendor": current_vendor
                })

            current_ip = ip_match.group(1)
            current_mac = None
            current_vendor = "Unknown"

        mac_match = re.search(
            r"MAC Address: ([0-9A-Fa-f:]+) \((.*?)\)",
            line
        )

        if mac_match:

            current_mac = mac_match.group(1)
            current_vendor = mac_match.group(2)

    if current_ip:

        devices.append({
            "ip": current_ip,
            "mac": current_mac,
            "vendor": current_vendor
        })

    return devices
