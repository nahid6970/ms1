from waitress import serve
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# This would typically be a database in a real application
costs = []

@app.route('/')
def index():
    return render_template('index.html', costs=costs)

@app.route('/add_cost', methods=['POST'])
def add_cost():
    item = request.form['item']
    amount = float(request.form['amount'])
    costs.append({'item': item, 'amount': amount})
    return redirect(url_for('index'))

if __name__ == '__main__':
    serve(app, host='0.0.0.0', port=9856)
