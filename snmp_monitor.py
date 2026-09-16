import subprocess
import os

SNMP_TARGET = os.getenv("POCKETNOC_SNMP_TARGET", "127.0.0.1:1161")
SNMP_COMMUNITY = os.getenv("POCKETNOC_SNMP_COMMUNITY")


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


def get_system_description():
    return snmp_get("1.3.6.1.2.1.1.1.0")


def get_system_uptime():
    return snmp_get("1.3.6.1.2.1.1.3.0")


def get_system_location():
    return snmp_get("1.3.6.1.2.1.1.6.0")


def get_system_contact():
    return snmp_get("1.3.6.1.2.1.1.4.0")


if __name__ == "__main__":
    print("System Description:")
    print(get_system_description())

    print("\nSystem Uptime:")
    print(get_system_uptime())

    print("\nSystem Location:")
    print(get_system_location())

    print("\nSystem Contact:")
    print(get_system_contact())
