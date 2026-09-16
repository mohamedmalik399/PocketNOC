import socket
import re
from datetime import datetime

from database import save_syslog

HOST = "0.0.0.0"
PORT = 5514

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((HOST, PORT))

print(f"Syslog server listening on UDP/{PORT}")

while True:
    data, address = sock.recvfrom(4096)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    message = data.decode(errors="replace").strip()

    match = re.match(r"<(\d+)>(.*)", message)

    if match:
        priority = int(match.group(1))
        syslog_message = match.group(2)

        facility = priority // 8
        severity = priority % 8

        save_syslog(
            timestamp,
            address[0],
            facility,
            severity,
            syslog_message
        )

        print(
            f"[{timestamp}] "
            f"SOURCE={address[0]} "
            f"FACILITY={facility} "
            f"SEVERITY={severity} "
            f"MESSAGE={syslog_message}"
        )

    else:
        print(
            f"[{timestamp}] "
            f"SOURCE={address[0]} "
            f"MESSAGE={message}"
        )
