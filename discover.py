import subprocess
import os
import re
from datetime import datetime

network = os.getenv("POCKETNOC_NETWORK", "192.0.2.0/24")
log_file = "logs/discovery.log"

timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

print("=" * 60)
print("POCKETNOC DEVICE DISCOVERY")
print(timestamp)
print("=" * 60)

result = subprocess.run(
    ["nmap", "-sn", network],
    capture_output=True,
    text=True
)

ips = re.findall(
    r"Nmap scan report for (\d+\.\d+\.\d+\.\d+)",
    result.stdout
)

with open(log_file, "a") as log:
    log.write(f"\n[{timestamp}] Discovery scan\n")

    if not ips:
        print("No devices found.")
        log.write("No devices found.\n")

    else:
        print(f"Found {len(ips)} active devices:\n")

        for ip in ips:
            print(ip)
            log.write(f"{ip}\n")

print("\nDiscovery complete.")
