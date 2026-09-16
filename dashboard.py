import os
from dotenv import load_dotenv

load_dotenv()

from database import (
    get_syslog,
    get_events,
    get_connection
)
from flask import Flask, jsonify, request
from functools import wraps
from network_engine import (
    get_network_data,
    get_uptime_data
)
from snmp_monitor import (
    get_system_description,
    get_system_uptime,
    get_system_location,
    get_system_contact
)

app = Flask(__name__)

USERNAME = os.getenv("POCKETNOC_USER", "admin")
PASSWORD = os.getenv("POCKETNOC_PASSWORD")

def check_auth(username, password):
    return username == USERNAME and password == PASSWORD


def requires_auth(f):

    @wraps(f)
    def decorated(*args, **kwargs):

        auth = request.authorization

        if not auth or not check_auth(
            auth.username,
            auth.password
        ):
            return (
                jsonify({
                    "error": "Authentication required"
                }),
                401,
                {
                    "WWW-Authenticate":
                    'Basic realm="PocketNOC"'
                }
            )

        return f(*args, **kwargs)

    return decorated


@app.route("/api/snmp/interfaces")
@requires_auth
def snmp_interfaces_api():

    connection = get_connection()

    rows = connection.execute(
        """
        SELECT
            timestamp,
            interface_index,
            interface_name,
            status,
            rx_bytes,
            tx_bytes,
            rx_bps,
            tx_bps
        FROM snmp_interface_measurements
        ORDER BY id DESC
        LIMIT 200
        """
    ).fetchall()

    connection.close()

    return {
        "measurements": [dict(row) for row in rows]
    }

@app.route("/api/snmp")
@requires_auth
def snmp_info():
    return {
        "description": get_system_description(),
        "uptime": get_system_uptime(),
        "location": get_system_location(),
        "contact": get_system_contact()
    }

@app.route("/api/syslog")
@requires_auth
def api_syslog():
    return jsonify(get_syslog())

@app.route("/api/devices")
@requires_auth
def get_devices():
    return jsonify(get_network_data())


@app.route("/api/inventory")
@requires_auth
def get_inventory():
    return jsonify(get_network_data())

@app.route("/api/events")
@requires_auth
def get_events():

    try:
        with open("logs/events.log", "r") as log:
            lines = log.readlines()

        events = []

        for line in reversed(lines[-50:]):
            events.append(line.strip())

        return jsonify(events)

    except FileNotFoundError:
        return jsonify([])

@app.route("/api/alerts")
@requires_auth
def get_alerts():
    try:
        with open("logs/alerts.log", "r") as alert_log:
            lines = alert_log.readlines()

        alerts = []

        for line in reversed(lines[-50:]):
            alerts.append(line.strip())

        return jsonify(alerts)

    except FileNotFoundError:
        return jsonify([])

@app.route("/api/uptime")
@requires_auth
def get_uptime():

    return jsonify(
        get_uptime_data()
    )

@app.route("/api/measurements")
@requires_auth
def get_measurements():
    import sqlite3

    connection = sqlite3.connect("pocketnoc.db")
    connection.row_factory = sqlite3.Row

    rows = connection.execute("""
        SELECT
            timestamp,
            device,
            service,
            state
        FROM measurements
        ORDER BY id DESC
        LIMIT 100
    """).fetchall()

    connection.close()

    return jsonify([dict(row) for row in rows])

@app.route("/api/availability")
@requires_auth
def get_availability():
    import sqlite3

    connection = sqlite3.connect("pocketnoc.db")
    connection.row_factory = sqlite3.Row

    rows = connection.execute("""
        SELECT
            device,
            service,
            COUNT(*) AS total,
            SUM(CASE WHEN state = 'UP' THEN 1 ELSE 0 END) AS up_count
        FROM measurements
        GROUP BY device, service
    """).fetchall()

    connection.close()

    availability = []

    for row in rows:
        total = row["total"]
        up_count = row["up_count"]

        percentage = (
            (up_count / total) * 100
            if total > 0
            else 0
        )

        availability.append({
            "device": row["device"],
            "service": row["service"],
            "total_measurements": total,
            "up_measurements": up_count,
            "availability": round(percentage, 2)
        })

    return jsonify(availability)

@app.route("/")
@requires_auth
def home():
    return """
    <!DOCTYPE html>
    <html>

    <head>
        <meta charset="UTF-8">
        <title>PocketNOC</title>

        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

        <style>

    * {
        box-sizing: border-box;
    }

    body {
        font-family: Arial, sans-serif;
        margin: 0;
        background: #f4f6f8;
        color: #222;
    }

    .header {
        background: #1f2937;
        color: white;
        padding: 25px 35px;
        border-bottom: 4px solid #374151;
    }

    .header h1 {
        margin: 0;
        font-size: 28px;
        letter-spacing: 1px;
    }

    .subtitle {
        margin: 6px 0 0;
        color: #d1d5db;
        font-size: 14px;
    }

    .container {
        max-width: 1500px;
        margin: auto;
        padding: 25px 35px;
    }

    .section-title {
        margin-top: 30px;
        margin-bottom: 15px;
        font-size: 20px;
    }

    .health-summary {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 18px;
        margin-bottom: 30px;
    }

    .counter {
        background: white;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #e5e7eb;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }

    .counter-title {
        color: #6b7280;
        font-size: 13px;
        font-weight: bold;
        letter-spacing: 0.5px;
    }

    .counter-value {
        font-size: 32px;
        font-weight: bold;
        margin-top: 8px;
    }

    .health-label {
        font-size: 12px;
        color: #6b7280;
        margin-top: 5px;
    }

    .section {
        margin-top: 30px;
        margin-bottom: 30px;
    }

    table {
        border-collapse: collapse;
        width: 100%;
        background: white;
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }

    th, td {
        border-bottom: 1px solid #e5e7eb;
        padding: 12px;
        text-align: left;
    }

    th {
        background: #eef0f2;
        font-size: 13px;
    }

    tr:last-child td {
        border-bottom: none;
    }

    .status-up {
        color: green;
        font-weight: bold;
    }

    .status-down {
        color: red;
        font-weight: bold;
    }

    .status-na {
        color: #777;
    }

    .chart-container {
        background: white;
        padding: 20px;
        margin-top: 15px;
        border-radius: 10px;
        border: 1px solid #e5e7eb;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }

    .two-column {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 20px;
    }

    .card {
        background: white;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #e5e7eb;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        margin-top: 15px;
    }

    .card h2 {
        margin-top: 0;
    }

    select {
        padding: 8px 12px;
        border-radius: 6px;
        border: 1px solid #ccc;
        background: white;
    }

    @media (max-width: 900px) {

        .health-summary {
            grid-template-columns: repeat(2, 1fr);
        }

        .two-column {
            grid-template-columns: 1fr;
        }

    }

    @media (max-width: 600px) {

        .health-summary {
            grid-template-columns: 1fr;
        }

        .container {
            padding: 15px;
        }

        .header {
            padding: 20px;
        }

        .header h1 {
            font-size: 22px;
        }

    }

</style>


    </head>


    <body>


         <div class="header">

             <h1>POCKETNOC NETWORK MONITOR</h1>

             <p class="subtitle">
                 Network Operations Center — Real-Time Monitoring
             </p>

        </div>

        <div class="container">

        <h2 class="section-title">Network Health Summary</h2>

            <div class="health-summary">

            <div class="counter">
                <div class="counter-title">
                    TOTAL DEVICES
                </div>

                <div class="counter-value" id="total-devices">
                    0
                </div>
            </div>


            <div class="counter">
                <div class="counter-title">
                    DEVICES UP
                </div>

                <div class="counter-value" id="devices-up">
                    0
                </div>
            </div>


            <div class="counter">
                <div class="counter-title">
                    DEVICES DOWN
                </div>

                <div class="counter-value" id="devices-down">
                    0
                </div>
            </div>


            <div class="counter">
                <div class="counter-title">
                    SSH 8022 UP
                </div>

                <div class="counter-value" id="ssh-up">
                    0
                </div>
            </div>


        </div>

        <table>

            <thead>

                <tr>
                    <th>IP Address</th>
                    <th>MAC Address</th>
                    <th>Vendor</th>
                    <th>ICMP</th>
                    <th>TCP 8022</th>
                </tr>

            </thead>


            <tbody id="device-table"></tbody>

        </table>

        <h2>Service Availability</h2>

        <table>

        <thead>

        <tr>
            <th>Service</th>
            <th>Current State</th>
            <th>Uptime</th>
            <th>Downtime</th>
            <th>Last Change</th>
        </tr>

        </thead>

       <tbody id="uptime-table"></tbody>

       </table>

       <br>

        <h2>Service Availability Percentage</h2>

	<div id="availabilitySummary">
    	Loading...
	</div>

        <div class="section">
   	<h2>SNMP Information</h2>

    	<table>
        <tr>
            <th>System Description</th>
            <td id="snmp-description">Loading...</td>
        </tr>

        <tr>
            <th>System Uptime</th>
            <td id="snmp-uptime">Loading...</td>
        </tr>

        <tr>
            <th>Location</th>
            <td id="snmp-location">Loading...</td>
        </tr>

        <tr>
            <th>Contact</th>
            <td id="snmp-contact">Loading...</td>
        </tr>
    	</table>
	</div>

       <h2>Historical Availability</h2>

        <label for="serviceSelector">Select service:</label>

        <select id="serviceSelector" onchange="updateAvailabilityChart()">
                <option value="">Loading...</option>
        </select>

        <div style="width: 100%; max-width: 1000px;">
            <canvas id="availabilityChart"></canvas>
        </div>

        <div class="card">
        <h2>SNMP Traffic — wlan0</h2>

        <canvas id="snmpTrafficChart"></canvas>
        </div>

        <h2>Syslog</h2>

	<table>
    	<thead>
        <tr>
            <th>Time</th>
            <th>Source</th>
            <th>Severity</th>
            <th>Message</th>
        </tr>
    	</thead>

    	<tbody id="syslogTable">
    	</tbody>
	</table>

        <h2>Active Alerts</h2>

	<div id="alerts">
    		Loading...
	</div>

       <h2>Event History</h2>

           <div id="event-list">
                Loading events...
           </div>

         <br>


        <script>
        async function updateSNMP() {

    try {

        const response = await fetch("/api/snmp");
        const data = await response.json();

        document.getElementById("snmp-description").textContent =
            data.description || "N/A";

        document.getElementById("snmp-uptime").textContent =
            data.uptime || "N/A";

        document.getElementById("snmp-location").textContent =
            data.location || "N/A";

        document.getElementById("snmp-contact").textContent =
            data.contact || "N/A";

    } catch (error) {

        console.error("SNMP error:", error);

    }
}

         async function updateSNMPTraffic() {

    try {

        const response = await fetch("/api/snmp/interfaces");
        const data = await response.json();

        const measurements = data.measurements
            .filter(item => item.interface_name === "wlan0")
            .reverse();

        console.log("SNMP wlan0 measurements:", measurements);

        if (measurements.length === 0) {
            console.log("No wlan0 SNMP measurements found");
            return;
        }

        const labels = measurements.map(
            item => item.timestamp
        );

        const rxData = measurements.map(
            item => Number(item.rx_bps) || 0
        );

        const txData = measurements.map(
            item => Number(item.tx_bps) || 0
        );

        const canvas = document.getElementById(
            "snmpTrafficChart"
        );

        if (!canvas) {
            console.error(
                "Canvas snmpTrafficChart not found"
            );
            return;
        }

        const ctx = canvas.getContext("2d");

        if (window.pocketNOCSnmpChart) {
            window.pocketNOCSnmpChart.destroy();
        }

        window.pocketNOCSnmpChart = new Chart(
            ctx,
            {
                type: "line",

                data: {
                    labels: labels,

                    datasets: [
                        {
                            label: "RX bps",
                            data: rxData,
                            tension: 0.2
                        },
                        {
                            label: "TX bps",
                            data: txData,
                            tension: 0.2
                        }
                    ]
                },

                options: {
                    responsive: true,

                    scales: {
                        y: {
                            beginAtZero: true,
                            title: {
                                display: true,
                                text: "Bits per second"
                            }
                        }
                    }
                }
            }
        );

    } catch (error) {

        console.error(
            "SNMP traffic error:",
            error
        );
    }
}

            async function updateSyslog() {
    const response = await fetch("/api/syslog");
    const logs = await response.json();

    const table = document.getElementById("syslogTable");

    table.innerHTML = "";

    const severityNames = {
        0: "EMERGENCY",
        1: "ALERT",
        2: "CRITICAL",
        3: "ERROR",
        4: "WARNING",
        5: "NOTICE",
        6: "INFO",
        7: "DEBUG"
    };

    logs.forEach(log => {
        const row = document.createElement("tr");

        const severity =
            severityNames[log.severity] || "UNKNOWN";

        row.innerHTML = `
            <td>${log.timestamp}</td>
            <td>${log.source_ip}</td>
            <td>${severity}</td>
            <td>${log.message}</td>
        `;

        table.appendChild(row);
    });
}

            async function updateAlerts() {
 		   try {
        const response = await fetch("/api/alerts");
        const alerts = await response.json();

        const container =
            document.getElementById("alerts");

        if (alerts.length === 0) {
            container.innerHTML =
                "<p>No alerts.</p>";
            return;
        }

        container.innerHTML = "";

        alerts.forEach(alert => {
            const item = document.createElement("div");

            item.style.padding = "12px";
            item.style.margin = "8px 0";
            item.style.border = "1px solid #ccc";
            item.style.borderRadius = "8px";

            item.textContent = "🚨 " + alert;

            container.appendChild(item);
        });

    } catch (error) {
        console.error(
            "Failed to load alerts:",
            error
        );
    }
}

            function formatTCPServices(device) {
    		if (!device.tcp_services) {
        		return "N/A";
    		}

    		const services = Object.entries(device.tcp_services);

    		if (services.length === 0) {
        		return "None";
    		}

    		return services.map(([name, data]) => {
        		return `${name} : ${data.port} — ${data.state}`;
    		}).join("<br>");
	    }

            async function loadDevices() {

                const response = await fetch("/api/devices");

                const devices = await response.json();


                /*
                 * Calculate dashboard statistics
                 */

                const total = devices.length;

                const up = devices.filter(
                    device => device.icmp === "UP"
                ).length;

                const down = devices.filter(
                    device => device.icmp === "DOWN"
                ).length;

                const sshUp = devices.filter(
                    device => device.tcp_8022 === "UP"
                ).length;


                /*
                 * Update counters
                 */

                document.getElementById(
                    "total-devices"
                ).textContent = total;

                document.getElementById(
                    "devices-up"
                ).textContent = up;

                document.getElementById(
                    "devices-down"
                ).textContent = down;

                document.getElementById(
                    "ssh-up"
                ).textContent = sshUp;


                /*
                 * Update device table
                 */

                const table =
                    document.getElementById("device-table");

                table.innerHTML = "";


                devices.forEach(device => {

                    const row =
                        document.createElement("tr");


                    let icmpClass = "";

                    if (device.icmp === "UP") {
                        icmpClass = "status-up";
                    }

                    else if (device.icmp === "DOWN") {
                        icmpClass = "status-down";
                    }

                    else {
                        icmpClass = "status-na";
                    }


                    let tcpClass = "";

                    if (device.tcp_8022 === "UP") {
                        tcpClass = "status-up";
                    }

                    else if (device.tcp_8022 === "DOWN") {
                        tcpClass = "status-down";
                    }

                    else {
                        tcpClass = "status-na";
                    }


                    row.innerHTML = `

                        <td>${device.ip}</td>

                        <td>
                            ${device.mac || "Unknown"}
                        </td>

                        <td>
                            ${device.vendor}
                        </td>

                        <td class="${icmpClass}">
                            ${device.icmp}
                        </td>

                        <td class="${tcpClass}">
                            ${formatTCPServices(device)}
                        </td>

                    `;


                    table.appendChild(row);

                });

            }


             /*
             * Initial load
             */

            loadDevices();
            updateAlerts();
            updateSyslog();
            updateSNMP();
            updateSNMPTraffic();

            /*
             * Refresh every 5 seconds
             */

            setInterval(loadDevices, 5000);
            setInterval(updateAlerts, 5000);
            setInterval(updateSyslog, 5000);
            setInterval(updateSNMP, 5000);
            setInterval(updateSNMPTraffic, 5000);
        </script>

        <script>

        async function loadEvents() {

        const response =
            await fetch("/api/events");

        const events =
            await response.json();

        const eventList =
            document.getElementById("event-list");

        if (events.length === 0) {

            eventList.innerHTML =
                "No events recorded.";

            return;
        }


        eventList.innerHTML = "";


        events.forEach(event => {

            const item =
                document.createElement("div");

            item.style.padding = "10px";

            item.style.borderBottom =
                "1px solid #ddd";

            item.textContent = event;

            eventList.appendChild(item);

        });

        }


        loadEvents();

        setInterval(loadEvents,5000);

        </script>

        <script>

	async function loadUptime() {

    	const response =
        await fetch("/api/uptime");

    	const data =
        await response.json();

    	const table =
        document.getElementById(
            "uptime-table"
        );

    	table.innerHTML = "";


    	Object.entries(data).forEach(
        ([service, stats]) => {

            const total =
                stats.up_seconds +
                stats.down_seconds;


            let availability = 0;


            if (total > 0) {

                availability =
                    (
                        stats.up_seconds /
                        total
                    ) * 100;

            }


            const row =
                document.createElement("tr");


            row.innerHTML = `

                <td>${service}</td>

                <td>
                    ${stats.state}
                </td>

                <td>
                    ${availability.toFixed(2)}%
                </td>

                <td>
                    ${stats.down_seconds.toFixed(0)} sec
                </td>

                <td>
                    ${stats.last_change}
                </td>

            `;


            table.appendChild(row);

            }
    	    );

	    }


      	    loadUptime();

            setInterval(loadUptime,5000);

            async function updateAvailabilitySummary() {
    try {
        const response = await fetch("/api/availability");
        const data = await response.json();

        const container =
            document.getElementById("availabilitySummary");

        if (data.length === 0) {
            container.innerHTML = "No availability data yet.";
            return;
        }

        container.innerHTML = "";

        data.forEach(item => {
            const card = document.createElement("div");

            card.style.padding = "15px";
            card.style.margin = "10px 0";
            card.style.border = "1px solid #ccc";
            card.style.borderRadius = "8px";

            card.innerHTML = `
                <strong>${item.device}</strong>
                — ${item.service}
                <br>
                Availability:
                <strong>${item.availability}%</strong>
                <br>
                Measurements:
                ${item.up_measurements}/${item.total_measurements}
            `;

            container.appendChild(card);
        });

    } catch (error) {
        console.error(
            "Failed to load availability:",
            error
        );
    }
}

            let availabilityChart = null;

	    async function updateAvailabilityChart() {
        try {
        const response = await fetch("/api/measurements");
        const measurements = await response.json();

        const selector = document.getElementById("serviceSelector");

        const services = [
            ...new Set(
                measurements.map(
                    item => `${item.device} ${item.service}`
                )
            )
        ];

        const currentSelection = selector.value;

        selector.innerHTML = "";

        services.forEach(service => {
            const option = document.createElement("option");
            option.value = service;
            option.textContent = service;
            selector.appendChild(option);
        });

        if (services.includes(currentSelection)) {
            selector.value = currentSelection;
        }

        if (!selector.value && services.length > 0) {
            selector.value = services[0];
        }

        const selectedService = selector.value;

        const filtered = measurements
            .filter(item =>
                `${item.device} ${item.service}` === selectedService
            )
            .reverse();

        const labels = filtered.map(
            item => item.timestamp
        );

        const values = filtered.map(
            item => item.state === "UP" ? 1 : 0
        );

        const ctx = document.getElementById(
            "availabilityChart"
        );

        if (availabilityChart) {
            availabilityChart.destroy();
        }

        availabilityChart = new Chart(ctx, {
            type: "line",

            data: {
                labels: labels,

                datasets: [{
                    label: selectedService,
                    data: values,
                    stepped: true,
                    fill: false
                }]
            },

            options: {
                responsive: true,

                scales: {
                    y: {
                        min: 0,
                        max: 1,
                        ticks: {
                            stepSize: 1,

                            callback: function(value) {
                                return value === 1
                                    ? "UP"
                                    : "DOWN";
                            }
                        }
                    }
                }
            }
        });

    } catch (error) {
        console.error(
            "Failed to load measurements:",
            error
        );
    }
}
        updateAvailabilityChart();
        updateAvailabilitySummary();

        setInterval(updateAvailabilityChart, 5000);
        setInterval(updateAvailabilitySummary, 5000);

    </script>

    </div>
    </body>

    </html>
    """

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=8080
    )
