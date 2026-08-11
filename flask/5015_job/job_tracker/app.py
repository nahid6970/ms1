import json
import os
from datetime import datetime, date
from flask import Flask, render_template, request, redirect, url_for, jsonify

app = Flask(__name__)

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_FILE = os.path.join(BASE_DIR, 'jobs_data.json')

def load_data():
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def calculate_days_left(deadline_str):
    if not deadline_str:
        return None
    try:
        deadline = datetime.strptime(deadline_str, '%Y-%m-%d').date()
        today = date.today()
        days_left = (deadline - today).days
        return days_left
    except:
        return None

@app.route('/')
def index():
    sort_by = request.args.get('sort_by', 'deadline')
    order = request.args.get('order', 'asc')
    query = request.args.get('query')
    status_filter = request.args.get('status_filter', 'all')
    hide_past_deadlines = request.args.get('hide_past', 'false') == 'true'

    jobs = load_data()

    # Add days_left calculation for each job
    for job in jobs:
        job['days_left'] = calculate_days_left(job.get('deadline'))

    # Filter jobs based on query
    if query:
        jobs = [job for job in jobs if query.lower() in job['company'].lower() or 
                query.lower() in job['position'].lower()]

    # Filter by status
    if status_filter != 'all':
        jobs = [job for job in jobs if job.get('status', '').lower().replace(' ', '-') == status_filter.lower()]

    # Filter past deadlines
    if hide_past_deadlines:
        jobs = [job for job in jobs if job['days_left'] is None or job['days_left'] >= 0]

    # Sort jobs
    if sort_by == 'company':
        jobs.sort(key=lambda x: x['company'].lower(), reverse=(order == 'desc'))
    elif sort_by == 'position':
        jobs.sort(key=lambda x: x['position'].lower(), reverse=(order == 'desc'))

    elif sort_by == 'applied_date':
        jobs.sort(key=lambda x: x.get('applied_date', ''), reverse=(order == 'desc'))
    elif sort_by == 'deadline':
        jobs.sort(key=lambda x: x.get('deadline', '9999-12-31'), reverse=(order == 'desc'))
    elif sort_by == 'status':
        jobs.sort(key=lambda x: x.get('status', '').lower(), reverse=(order == 'desc'))

    next_order = 'desc' if order == 'asc' else 'asc'

    return render_template('index.html', jobs=jobs, sort_by=sort_by, order=order, 
                         next_order=next_order, query=query, status_filter=status_filter,
                         hide_past_deadlines=hide_past_deadlines)

@app.route('/add_job', methods=['GET', 'POST'])
def add_job():
    if request.method == 'POST':
        jobs = load_data()
        new_job = {
            'id': max([job['id'] for job in jobs], default=0) + 1,
            'company': request.form['company'],
            'position': request.form['position'],
            'job_url': request.form.get('job_url', ''),
            'applied_date': request.form.get('applied_date', ''),
            'deadline': request.form.get('deadline', ''),
            'status': request.form.get('status', 'Interested'),
            'notes': request.form.get('notes', ''),
            'created_date': datetime.now().isoformat()
        }
        jobs.append(new_job)
        save_data(jobs)
        return redirect(url_for('index'))
    return render_template('add_job.html')

@app.route('/edit_job/<int:job_id>', methods=['GET', 'POST'])
def edit_job(job_id):
    jobs = load_data()
    job = next((j for j in jobs if j['id'] == job_id), None)
    if not job:
        return 'Job not found', 404
    
    if request.method == 'POST':
        job['company'] = request.form['company']
        job['position'] = request.form['position']
        job['job_url'] = request.form.get('job_url', '')
        job['applied_date'] = request.form.get('applied_date', '')
        job['deadline'] = request.form.get('deadline', '')
        job['status'] = request.form.get('status', 'Interested')
        job['notes'] = request.form.get('notes', '')
        save_data(jobs)
        return redirect(url_for('index'))
    else:
        return jsonify(job)

@app.route('/delete_job/<int:job_id>')
def delete_job(job_id):
    jobs = load_data()
    jobs = [j for j in jobs if j['id'] != job_id]
    save_data(jobs)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, port=5015)