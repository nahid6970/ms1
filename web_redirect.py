from flask import Flask, redirect, send_file

app = Flask(__name__)

# Port 7710: Send local file
@app.route('/')
def serve_local_file():
    return send_file(r'C:\ms1\archlinux\os.sh', as_attachment=True)

# Run the apps on their respective ports
if __name__ == '__main__':
    from threading import Thread

    def run_app(app, port):
        app.run(host='0.0.0.0', port=port, debug=False)

    Thread(target=run_app, args=(app, 7710)).start()