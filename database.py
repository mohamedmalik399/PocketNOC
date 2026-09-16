import sqlite3


DB_FILE = "pocketnoc.db"


def get_connection():

    connection = sqlite3.connect(DB_FILE)

    connection.row_factory = sqlite3.Row

    return connection


def init_database():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            device TEXT NOT NULL,
            service TEXT NOT NULL,
            old_state TEXT NOT NULL,
            new_state TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS uptime (
            device TEXT NOT NULL,
            service TEXT NOT NULL,
            state TEXT NOT NULL,
            up_seconds REAL DEFAULT 0,
            down_seconds REAL DEFAULT 0,
            last_change TEXT,
            PRIMARY KEY (device, service)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS measurements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            device TEXT NOT NULL,
            service TEXT NOT NULL,
            state TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS snmp_interface_measurements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            interface_index INTEGER NOT NULL,
            interface_name TEXT NOT NULL,
            status TEXT NOT NULL,
            rx_bytes INTEGER,
            tx_bytes INTEGER,
            rx_bps REAL,
            tx_bps REAL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            device TEXT NOT NULL,
            service TEXT NOT NULL,
            status TEXT NOT NULL,
            message TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS syslog (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            source_ip TEXT NOT NULL,
            facility INTEGER,
            severity INTEGER,
            message TEXT NOT NULL
        )
    """)

    connection.commit()
    connection.close()


def save_alert(timestamp, device, service, status, message):
    connection = get_connection()

    connection.execute(
        """
        INSERT INTO alerts
        (
            timestamp,
            device,
            service,
            status,
            message
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            timestamp,
            device,
            service,
            status,
            message
        )
    )

    connection.commit()
    connection.close()


def get_alerts(active_only=False):
    connection = get_connection()

    if active_only:
        rows = connection.execute(
            """
            SELECT
                timestamp,
                device,
                service,
                status,
                message
            FROM alerts
            WHERE status = 'ACTIVE'
            ORDER BY id DESC
            """
        ).fetchall()
    else:
        rows = connection.execute(
            """
            SELECT
                timestamp,
                device,
                service,
                status,
                message
            FROM alerts
            ORDER BY id DESC
            LIMIT 50
            """
        ).fetchall()

    connection.close()

    return [dict(row) for row in rows]

def save_syslog(timestamp, source_ip, facility, severity, message):
    connection = get_connection()

    connection.execute(
        """
        INSERT INTO syslog
        (
            timestamp,
            source_ip,
            facility,
            severity,
            message
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            timestamp,
            source_ip,
            facility,
            severity,
            message
        )
    )

    connection.commit()
    connection.close()

def save_event(
    timestamp,
    device,
    service,
    old_state,
    new_state
):

    connection = get_connection()

    connection.execute(
        """
        INSERT INTO events
        (
            timestamp,
            device,
            service,
            old_state,
            new_state
        )

        VALUES (?, ?, ?, ?, ?)
        """,

        (
            timestamp,
            device,
            service,
            old_state,
            new_state
        )
    )

    connection.commit()

    connection.close()


def get_events(limit=50):

    connection = get_connection()

    rows = connection.execute(
        """
        SELECT
            timestamp,
            device,
            service,
            old_state,
            new_state

        FROM events

        ORDER BY id DESC

        LIMIT ?
        """,

        (limit,)
    ).fetchall()

    connection.close()

    return [dict(row) for row in rows]


def save_uptime(
    device,
    service,
    state,
    up_seconds,
    down_seconds,
    last_change
):

    connection = get_connection()

    connection.execute(
        """
        INSERT INTO uptime
        (
            device,
            service,
            state,
            up_seconds,
            down_seconds,
            last_change
        )

        VALUES (?, ?, ?, ?, ?, ?)

        ON CONFLICT(device, service)

        DO UPDATE SET

            state = excluded.state,

            up_seconds =
                excluded.up_seconds,

            down_seconds =
                excluded.down_seconds,

            last_change =
                excluded.last_change
        """,

        (
            device,
            service,
            state,
            up_seconds,
            down_seconds,
            last_change
        )
    )

    connection.commit()

    connection.close()


def get_uptime():

    connection = get_connection()

    rows = connection.execute(
        """
        SELECT
            device,
            service,
            state,
            up_seconds,
            down_seconds,
            last_change

        FROM uptime
        """
    ).fetchall()

    connection.close()

    return [dict(row) for row in rows]


def save_measurement(
    timestamp,
    device,
    service,
    state
):

    connection = get_connection()

    connection.execute(
        """
        INSERT INTO measurements
        (
            timestamp,
            device,
            service,
            state
        )

        VALUES (?, ?, ?, ?)
        """,

        (
            timestamp,
            device,
            service,
            state
        )
    )

    connection.commit()

    connection.close()

def save_snmp_interface_measurement(
    timestamp,
    interface_index,
    interface_name,
    status,
    rx_bytes,
    tx_bytes,
    rx_bps,
    tx_bps
):
    connection = get_connection()

    connection.execute(
        """
        INSERT INTO snmp_interface_measurements
        (
            timestamp,
            interface_index,
            interface_name,
            status,
            rx_bytes,
            tx_bytes,
            rx_bps,
            tx_bps
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            timestamp,
            interface_index,
            interface_name,
            status,
            rx_bytes,
            tx_bytes,
            rx_bps,
            tx_bps
        )
    )

    connection.commit()
    connection.close()

def get_syslog(limit=50):
    connection = get_connection()

    rows = connection.execute(
        """
        SELECT
            timestamp,
            source_ip,
            facility,
            severity,
            message
        FROM syslog
        ORDER BY id DESC
        LIMIT ?
        """,
        (limit,)
    ).fetchall()

    connection.close()

    return [dict(row) for row in rows]
