from flask import Flask, render_template, request

app = Flask(__name__)

# Variable to store shared text
shared_text = ""

@app.route('/', methods=['GET', 'POST'])
def index():
    global shared_text
    if request.method == 'POST':
        # Get the text from the form
        shared_text = request.form['text']
    
    # Render the template with the shared text
    return render_template('index.html', shared_text=shared_text)

if __name__ == '__main__':
    # Replace '192.168.0.101' with your local IP if necessary
    app.run(host='0.0.0.0', port=5000, debug=True)
