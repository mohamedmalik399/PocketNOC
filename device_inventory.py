import subprocess
import os
import re
from datetime import datetime

NETWORK = os.getenv("POCKETNOC_NETWORK", "192.0.2.0/24")
LOG_FILE = "logs/device_inventory.log"


def discover_devices():

    result = subprocess.run(
        ["nmap", "-sn", NETWORK],
        capture_output=True,
        text=True
    )

    return result.stdout


def parse_devices(output):

    devices = []

    blocks = re.split(
        r"(?=Nmap scan report for )",
        output
    )

    for block in blocks:

        ip_match = re.search(
            r"Nmap scan report for (\d+\.\d+\.\d+\.\d+)",
            block
        )

        mac_match = re.search(
            r"MAC Address: ([0-9A-Fa-f:]+)(?: \((.*?)\))?",
            block
        )

        if ip_match:

            ip = ip_match.group(1)

            if mac_match:
                mac = mac_match.group(1)
                vendor = mac_match.group(2) or "Unknown"
            else:
                mac = "Unknown"
                vendor = "Unknown"

            devices.append(
                {
                    "ip": ip,
                    "mac": mac,
                    "vendor": vendor
                }
            )

    return devices


print("=" * 70)
print("POCKETNOC DEVICE INVENTORY")
print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
print("=" * 70)

output = discover_devices()

devices = parse_devices(output)

print(
    f"\nFound {len(devices)} devices\n"
)

print(
    f"{'IP Address':15} "
    f"{'MAC Address':20} "
    f"Vendor"
)

print("-" * 70)

with open(LOG_FILE, "a") as log:

    timestamp = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    for device in devices:

        print(
            f"{device['ip']:15} "
            f"{device['mac']:20} "
            f"{device['vendor']}"
        )

        log.write(
            f"{timestamp} | "
            f"{device['ip']} | "
            f"{device['mac']} | "
            f"{device['vendor']}\n"
        )

print("\nInventory complete.")
