from flask import Flask, jsonify, render_template_string
import subprocess
import json

app = Flask(__name__)

def get_battery_info():
    try:
        # Run the Termux API command to get battery status
        result = subprocess.run(['termux-battery-status'], capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)

        return {
            "level": data.get("percentage"),
            "status": data.get("status"),
            "temperature": data.get("temperature", 0),
            "voltage": data.get("voltage"),
            "plugged": "PLUGGED" if data.get("plugged") else "UNPLUGGED"
        }

    except subprocess.CalledProcessError as e:
        return {"error": f"Failed to run termux-battery-status: {e}"}
    except json.JSONDecodeError:
        return {"error": "Failed to parse termux-battery-status output"}
    except Exception as e:
        return {"error": str(e)}

@app.route('/')
def index():
    return render_template_string('''
        <h1>Battery Info</h1>
        <p><a href="/battery">View Battery Info</a></p>
    ''')

@app.route('/battery')
def battery():
    info = get_battery_info()
    return jsonify(info)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
