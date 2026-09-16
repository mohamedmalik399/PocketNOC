import subprocess
import os
import re


SNMP_TARGET = os.getenv("POCKETNOC_SNMP_TARGET", "127.0.0.1:1161")
SNMP_COMMUNITY = os.getenv("POCKETNOC_SNMP_COMMUNITY")


IF_DESCR_OID = "1.3.6.1.2.1.2.2.1.2"
IF_OPER_STATUS_OID = "1.3.6.1.2.1.2.2.1.8"
IF_IN_OCTETS_OID = "1.3.6.1.2.1.2.2.1.10"
IF_OUT_OCTETS_OID = "1.3.6.1.2.1.2.2.1.16"


def snmp_walk(oid):

    result = subprocess.run(
        [
            "snmpwalk",
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
        return []

    return result.stdout.splitlines()


def snmp_get(oid):

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

    return result.stdout.strip()


def discover_interfaces():

    lines = snmp_walk(IF_DESCR_OID)

    interfaces = []

    for line in lines:

        match = re.search(
            r"ifDescr\.(\d+) = STRING: (.+)",
            line
        )

        if match:

            index = int(match.group(1))
            name = match.group(2)

            interfaces.append({
                "index": index,
                "name": name
            })

    return interfaces


def get_interface_status(index):

    oid = f"{IF_OPER_STATUS_OID}.{index}"

    result = snmp_get(oid)

    if result is None:
        return "UNKNOWN"

    if "up(1)" in result:
        return "UP"

    if "down(2)" in result:
        return "DOWN"

    return "UNKNOWN"


def get_counter(oid, index):

    result = snmp_get(
        f"{oid}.{index}"
    )

    if result is None:
        return None

    match = re.search(
        r"Counter\d+: (\d+)",
        result
    )

    if not match:
        return None

    return int(match.group(1))


def get_interface_data():

    interfaces = discover_interfaces()

    data = []

    for interface in interfaces:

        index = interface["index"]

        status = get_interface_status(index)

        rx_bytes = get_counter(
            IF_IN_OCTETS_OID,
            index
        )

        tx_bytes = get_counter(
            IF_OUT_OCTETS_OID,
            index
        )

        data.append({
            "index": index,
            "name": interface["name"],
            "status": status,
            "rx_bytes": rx_bytes,
            "tx_bytes": tx_bytes
        })

    return data


if __name__ == "__main__":

    interfaces = get_interface_data()

    print("SNMP Interface Monitor")
    print("======================")

    for interface in interfaces:

        print(
            f"{interface['index']:>2} "
            f"{interface['name']:<15} "
            f"{interface['status']:<7} "
            f"RX={interface['rx_bytes']} "
            f"TX={interface['tx_bytes']}"
        )
