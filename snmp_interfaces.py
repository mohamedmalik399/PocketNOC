import subprocess
import os
import re


SNMP_TARGET = "127.0.0.1:1161"
SNMP_COMMUNITY = os.getenv("POCKETNOC_SNMP_COMMUNITY")


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


def get_interfaces():
    lines = snmp_walk("1.3.6.1.2.1.2.2.1.2")

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


if __name__ == "__main__":

    interfaces = get_interfaces()

    print("SNMP Interfaces")
    print("----------------")

    for interface in interfaces:
        print(
            f"{interface['index']:>2} "
            f"{interface['name']}"
        )
