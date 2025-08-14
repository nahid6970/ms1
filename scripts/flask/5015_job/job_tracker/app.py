import json
import os
from datetime import datetime
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

@app.route('/')
def index():
    sort_by = request.args.get('sort_by', 'company')
    order = request.args.get('order', 'asc')
    query = request.args.get('query')
    status_filter = request.args.get('status_filter', 'all')

    jobs = load_data()

    # Filter jobs based on query
    if query:
        jobs = [job for job in jobs if query.lower() in job['company'].lower() or 
                query.lower() in job['position'].lower()]

    # Filter by status
    if status_filter != 'all':
        jobs = [job for job in jobs if job.get('status', '').lower() == status_filter.lower()]

    # Sort jobs
    if sort_by == 'company':
        jobs.sort(key=lambda x: x['company'].lower(), reverse=(order == 'desc'))
    elif sort_by == 'position':
        jobs.sort(key=lambda x: x['position'].lower(), reverse=(order == 'desc'))
    elif sort_by == 'salary':
        jobs.sort(key=lambda x: float(x.get('salary', 0)) if x.get('salary') else 0, reverse=(order == 'desc'))
    elif sort_by == 'applied_date':
        jobs.sort(key=lambda x: x.get('applied_date', ''), reverse=(order == 'desc'))
    elif sort_by == 'deadline':
        jobs.sort(key=lambda x: x.get('deadline', '9999-12-31'), reverse=(order == 'desc'))
    elif sort_by == 'status':
        jobs.sort(key=lambda x: x.get('status', '').lower(), reverse=(order == 'desc'))

    next_order = 'desc' if order == 'asc' else 'asc'

    return render_template('index.html', jobs=jobs, sort_by=sort_by, order=order, 
                         next_order=next_order, query=query, status_filter=status_filter)

@app.route('/add_job', methods=['GET', 'POST'])
def add_job():
    if request.method == 'POST':
        jobs = load_data()
        new_job = {
            'id': max([job['id'] for job in jobs], default=0) + 1,
            'company': request.form['company'],
            'position': request.form['position'],
            'location': request.form.get('location', ''),
            'salary': request.form.get('salary', ''),
            'job_url': request.form.get('job_url', ''),
            'applied': request.form.get('applied') == 'on',
            'applied_date': request.form.get('applied_date', ''),
            'deadline': request.form.get('deadline', ''),
            'paid_application': request.form.get('paid_application') == 'on',
            'application_fee': request.form.get('application_fee', ''),
            'status': request.form.get('status', 'Not Applied'),
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
        job['location'] = request.form.get('location', '')
        job['salary'] = request.form.get('salary', '')
        job['job_url'] = request.form.get('job_url', '')
        job['applied'] = request.form.get('applied') == 'on'
        job['applied_date'] = request.form.get('applied_date', '')
        job['deadline'] = request.form.get('deadline', '')
        job['paid_application'] = request.form.get('paid_application') == 'on'
        job['application_fee'] = request.form.get('application_fee', '')
        job['status'] = request.form.get('status', 'Not Applied')
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