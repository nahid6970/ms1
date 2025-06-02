from flask import Flask, jsonify, render_template_string
import subprocess
import json
import os

app = Flask(__name__)

# HTML template for the web page
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Android Device Info</title>
    <style>
        body {
            font-family: sans-serif;
            margin: 20px;
            background-color: #f4f4f4;
            color: #333;
        }
        .container {
            background-color: #fff;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        h1 {
            color: #007bff;
        }
        h2 {
            color: #0056b3;
            border-bottom: 1px solid #eee;
            padding-bottom: 5px;
            margin-top: 20px;
        }
        p {
            margin: 5px 0;
        }
        strong {
            color: #555;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Android Device Information</h1>

        <h2>Battery Info</h2>
        <p><strong>Status:</strong> {{ battery_info.status }}</p>
        <p><strong>Health:</strong> {{ battery_info.health }}</p>
        <p><strong>Percentage:</strong> {{ battery_info.percentage }}%</p>
        <p><strong>Temperature:</strong> {{ battery_info.temperature }}°C</p>
        <p><strong>Voltage:</strong> {{ battery_info.voltage }}mV</p>
        <p><strong>Technology:</strong> {{ battery_info.technology }}</p>

        <h2>Network Info</h2>
        <p><strong>IP Address:</strong> {{ network_info.ip_address }}</p>
        <p><strong>Gateway:</strong> {{ network_info.gateway }}</p>
        <p><strong>DNS Servers:</strong> {{ network_info.dns_servers }}</p>

        <h2>Storage Info</h2>
        <p><strong>Internal Storage Total:</strong> {{ storage_info.internal_total }}</p>
        <p><strong>Internal Storage Used:</strong> {{ storage_info.internal_used }}</p>
        <p><strong>Internal Storage Available:</strong> {{ storage_info.internal_available }}</p>
        {% if storage_info.sdcard_total %}
        <h2>SD Card Info</h2>
        <p><strong>SD Card Total:</strong> {{ storage_info.sdcard_total }}</p>
        <p><strong>SD Card Used:</strong> {{ storage_info.sdcard_used }}</p>
        <p><strong>SD Card Available:</strong> {{ storage_info.sdcard_available }}</p>
        {% endif %}

        <h2>Device Info</h2>
        <p><strong>Android Version:</strong> {{ device_info.android_version }}</p>
        <p><strong>Manufacturer:</strong> {{ device_info.manufacturer }}</p>
        <p><strong>Model:</strong> {{ device_info.model }}</p>
        <p><strong>Brand:</strong> {{ device_info.brand }}</p>
        <p><strong>Device:</strong> {{ device_info.device }}</p>
        <p><strong>Hardware:</strong> {{ device_info.hardware }}</p>
        <p><strong>Build ID:</strong> {{ device_info.build_id }}</p>
        <p><strong>Uptime:</strong> {{ device_info.uptime }}</p>
    </div>
</body>
</html>
"""

def get_battery_info():
    try:
        result = subprocess.run(['termux-battery-status'], capture_output=True, text=True, check=True)
        return json.loads(result.stdout)
    except Exception as e:
        return {"error": f"Could not get battery info: {e}"}

def get_network_info():
    info = {
        "ip_address": "N/A",
        "gateway": "N/A",
        "dns_servers": "N/A"
    }
    try:
        # Get IP address
        ip_result = subprocess.run(['ip', 'route', 'get', '1.1.1.1'], capture_output=True, text=True)
        if ip_result.returncode == 0:
            for line in ip_result.stdout.splitlines():
                if 'src' in line:
                    info['ip_address'] = line.split('src')[1].strip().split(' ')[0]
                if 'via' in line:
                    info['gateway'] = line.split('via')[1].strip().split(' ')[0]

        # Get DNS servers from resolv.conf
        if os.path.exists('/etc/resolv.conf'):
            with open('/etc/resolv.conf', 'r') as f:
                dns_servers = []
                for line in f:
                    if line.startswith('nameserver'):
                        dns_servers.append(line.split()[1])
                info['dns_servers'] = ', '.join(dns_servers) if dns_servers else "N/A"

    except Exception as e:
        info["error"] = f"Could not get network info: {e}"
    return info

def get_storage_info():
    info = {
        "internal_total": "N/A",
        "internal_used": "N/A",
        "internal_available": "N/A",
        "sdcard_total": None, # Will be set if found
        "sdcard_used": None,
        "sdcard_available": None
    }
    try:
        # Internal storage (Termux home directory's partition)
        df_output = subprocess.run(['df', '-h', '/data/data/com.termux/files/home'], capture_output=True, text=True, check=True)
        lines = df_output.stdout.splitlines()
        if len(lines) > 1:
            parts = lines[1].split()
            info['internal_total'] = parts[1]
            info['internal_used'] = parts[2]
            info['internal_available'] = parts[3]

        # SD card (common mount points)
        sdcard_paths = ['/sdcard', '/storage/emulated/0', '/mnt/sdcard']
        for path in sdcard_paths:
            if os.path.exists(path):
                try:
                    sd_df_output = subprocess.run(['df', '-h', path], capture_output=True, text=True, check=True)
                    sd_lines = sd_df_output.stdout.splitlines()
                    if len(sd_lines) > 1:
                        sd_parts = sd_lines[1].split()
                        info['sdcard_total'] = sd_parts[1]
                        info['sdcard_used'] = sd_parts[2]
                        info['sdcard_available'] = sd_parts[3]
                        break # Found one, no need to check others
                except Exception:
                    pass # Ignore if a specific path doesn't work

    except Exception as e:
        info["error"] = f"Could not get storage info: {e}"
    return info

def get_device_info():
    info = {
        "android_version": "N/A",
        "manufacturer": "N/A",
        "model": "N/A",
        "brand": "N/A",
        "device": "N/A",
        "hardware": "N/A",
        "build_id": "N/A",
        "uptime": "N/A"
    }
    try:
        # Using getprop for various system properties
        def get_prop(prop_name):
            try:
                result = subprocess.run(['getprop', prop_name], capture_output=True, text=True, check=True)
                return result.stdout.strip()
            except Exception:
                return "N/A"

        info['android_version'] = get_prop('ro.build.version.release')
        info['manufacturer'] = get_prop('ro.product.manufacturer')
        info['model'] = get_prop('ro.product.model')
        info['brand'] = get_prop('ro.product.brand')
        info['device'] = get_prop('ro.product.device')
        info['hardware'] = get_prop('ro.hardware')
        info['build_id'] = get_prop('ro.build.id')

        # Uptime
        uptime_result = subprocess.run(['uptime', '-p'], capture_output=True, text=True)
        if uptime_result.returncode == 0:
            info['uptime'] = uptime_result.stdout.strip().replace('up ', '')

    except Exception as e:
        info["error"] = f"Could not get device info: {e}"
    return info


@app.route('/')
def index():
    battery_info = get_battery_info()
    network_info = get_network_info()
    storage_info = get_storage_info()
    device_info = get_device_info()

    return render_template_string(
        HTML_TEMPLATE,
        battery_info=battery_info,
        network_info=network_info,
        storage_info=storage_info,
        device_info=device_info
    )

@app.route('/api/device_info')
def api_device_info():
    battery_info = get_battery_info()
    network_info = get_network_info()
    storage_info = get_storage_info()
    device_info = get_device_info()

    return jsonify({
        "battery": battery_info,
        "network": network_info,
        "storage": storage_info,
        "device": device_info
    })

if __name__ == '__main__':
    # You can change the host to '0.0.0.0' to make it accessible from other devices on your local network
    # For local access on the same device, '127.0.0.1' or 'localhost' is fine.
    app.run(host='0.0.0.0', port=5000, debug=True)