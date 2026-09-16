import subprocess
import os
import re
import time


SNMP_TARGET = "127.0.0.1:1161"
SNMP_COMMUNITY = os.getenv("POCKETNOC_SNMP_COMMUNITY")

WLAN_IFINDEX = 12


def get_counter(oid):
    result = subprocess.run(
        [
            "snmpget",
            "-v2c",
            "-c",
            SNMP_COMMUNITY,
            SNMP_TARGET,
            oid
        ],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        return None

    match = re.search(r"Counter\d+: (\d+)", result.stdout)

    if not match:
        return None

    return int(match.group(1))


def get_rx_bytes():
    oid = f"1.3.6.1.2.1.2.2.1.10.{WLAN_IFINDEX}"
    return get_counter(oid)


def get_tx_bytes():
    oid = f"1.3.6.1.2.1.2.2.1.16.{WLAN_IFINDEX}"
    return get_counter(oid)


def calculate_rate(old_bytes, new_bytes, seconds):
    if old_bytes is None or new_bytes is None:
        return None

    if seconds <= 0:
        return None

    difference = new_bytes - old_bytes

    if difference < 0:
        return None

    bits = difference * 8

    return bits / seconds


if __name__ == "__main__":

    old_rx = get_rx_bytes()
    old_tx = get_tx_bytes()

    print("Waiting 10 seconds...")
    time.sleep(10)

    new_rx = get_rx_bytes()
    new_tx = get_tx_bytes()

    rx_rate = calculate_rate(
        old_rx,
        new_rx,
        10
    )

    tx_rate = calculate_rate(
        old_tx,
        new_tx,
        10
    )

    print(f"RX: {rx_rate:.2f} bits/sec")
    print(f"TX: {tx_rate:.2f} bits/sec")
