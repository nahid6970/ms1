from flask import Flask, render_template_string
import subprocess
import json

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Battery Status</title>
    <style>
        body {
            background-color: #f4f4f4;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            font-family: sans-serif;
        }
        .battery-container {
            width: 250px;
            height: 120px;
            background: #ddd;
            border-radius: 10px;
            position: relative;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }
        .battery-tip {
            width: 20px;
            height: 40px;
            background: #ddd;
            position: absolute;
            right: -20px;
            top: 40px;
            border-radius: 2px;
        }
        .battery-fill {
            width: {{ battery_info.percentage }}%;
            height: 100%;
            background-color: {% if battery_info.percentage < 20 %}#dc3545{% elif battery_info.percentage < 50 %}#ffc107{% else %}#28a745{% endif %};
            border-radius: 10px 0 0 10px;
            transition: width 0.3s ease-in-out;
        }
        .battery-text {
            position: absolute;
            width: 100%;
            height: 100%;
            text-align: center;
            line-height: 120px;
            font-size: 2.5em;
            font-weight: bold;
            color: #333;
            pointer-events: none;
        }
    </style>
</head>
<body>
    <div class="battery-container">
        <div class="battery-fill"></div>
        <div class="battery-text">{{ battery_info.percentage }}%</div>
        <div class="battery-tip"></div>
    </div>
</body>
</html>
"""

def get_battery_info():
    try:
        result = subprocess.run(['termux-battery-status'], capture_output=True, text=True, check=True)
        return json.loads(result.stdout)
    except Exception as e:
        return {"percentage": 0, "error": str(e)}

@app.route('/')
def index():
    battery_info = get_battery_info()
    return render_template_string(HTML_TEMPLATE, battery_info=battery_info)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)
