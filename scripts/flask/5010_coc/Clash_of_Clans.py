from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import re

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///c:/msBackups/DataBase/Clash_of_Clans.db'  # Changed DB path for portability
db = SQLAlchemy(app)

# Models
class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    logo_url = db.Column(db.String(300), nullable=False)

class Event(db.Model):  # Renamed Match to Event
    id = db.Column(db.Integer, primary_key=True)
    team1_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    # team2_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False) # Removed team2
    event_link = db.Column(db.String(300), nullable=False) # Renamed game_link
    event_time = db.Column(db.DateTime, nullable=False) # Renamed game_time

    team1 = db.relationship('Team', foreign_keys=[team1_id])
    # team2 = db.relationship('Team', foreign_keys=[team2_id]) # Removed team2

@app.route('/')
def index():
    now = datetime.now()
    upcoming_events = Event.query.filter(Event.event_time >= now).order_by(Event.event_time).all() # Renamed variables
    past_events = Event.query.filter(Event.event_time < now).order_by(Event.event_time.desc()).limit(10).all() # Renamed variables
    return render_template('event_list.html', upcoming_events=upcoming_events, past_events=past_events) # Renamed template

@app.route('/add-event', methods=['GET', 'POST']) # Renamed route
def add_event(): # Renamed function
    if request.method == 'POST':
        team1_id = request.form['team1']
        # team2_id = request.form['team2'] # Removed team2
        event_link = request.form['event_link'] # Renamed variable
        duration = request.form['duration']

        # Parse the duration
        days, hours, minutes = 0, 0, 0

        if 'd' in duration:
            days = int(duration.split('d')[0])
        if 'h' in duration:
            hours = int(duration.split('d')[-1].split('h')[0])
        if 'm' in duration:
            minutes = int(duration.split('h')[-1].split('m')[0])

        # Calculate event time (current time + duration)
        event_time = datetime.now() + timedelta(days=days, hours=hours, minutes=minutes) # Renamed variable

        # Add event to the database
        event = Event(team1_id=team1_id,  event_link=event_link, event_time=event_time) # Removed team2
        db.session.add(event)
        db.session.commit()
        return redirect(url_for('index'))

    # Sort teams alphabetically by name
    teams = Team.query.order_by(Team.name).all()
    return render_template('event_form.html', teams=teams, action='Add') # Renamed template, added action

@app.route('/teams', methods=['GET', 'POST'])
def manage_teams():
    if request.method == 'POST':
        name = request.form['name']
        logo_url = request.form['logo_url']
        team = Team(name=name, logo_url=logo_url)
        db.session.add(team)
        db.session.commit()
        return redirect(url_for('manage_teams'))
    teams = Team.query.order_by(Team.name).all()
    return render_template('team_manager.html', teams=teams) # Renamed template

@app.route('/delete-event/<int:id>', methods=['POST']) # Renamed route
def delete_event(id): # Renamed function
    event = Event.query.get_or_404(id) # Renamed variable
    db.session.delete(event)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/delete-team/<int:id>', methods=['POST'])
def delete_team(id):
    team = Team.query.get_or_404(id)
    db.session.delete(team)
    db.session.commit()
    return redirect(url_for('manage_teams'))

@app.route('/edit-event/<int:event_id>', methods=['GET', 'POST']) # Renamed route, variable, and function
def edit_event(event_id):
    event = Event.query.get(event_id) # Renamed variable
    teams = Team.query.order_by(Team.name).all()

    if request.method == 'POST':
        team1_id = request.form['team1']
        # team2_id = request.form['team2'] # Removed team2
        event_link = request.form['event_link'] # Renamed variable
        duration = request.form['duration'].strip()

        # Parse the duration
        days, hours, minutes = 0, 0, 0

        d_match = re.search(r'(\d+)\s*d', duration)
        h_match = re.search(r'(\d+)\s*h', duration)
        m_match = re.search(r'(\d+)\s*m', duration)

        if d_match:
            days = int(d_match.group(1))
        if h_match:
            hours = int(h_match.group(1))
        if m_match:
            minutes = int(m_match.group(1))

        # Calculate new event time from now
        event_time = datetime.now() + timedelta(days=days, hours=hours, minutes=minutes) # Renamed variable

        # Update the event
        event.team1_id = team1_id
        # event.team2_id = team2_id # Removed team2
        event.event_link = event_link # Renamed variable
        event.event_time = event_time # Renamed variable

        db.session.commit()
        return redirect(url_for('index'))

    # This part runs only for GET (form load)
    now = datetime.now()
    remaining = event.event_time - now if event.event_time > now else timedelta(0) # Renamed variable
    days = remaining.days
    hours = remaining.seconds // 3600
    minutes = (remaining.seconds % 3600) // 60
    duration_str = f"{days}d {hours}h {minutes}m"

    return render_template('event_form.html', event=event, teams=teams, duration=duration_str, action='Edit') # Renamed template, added action

@app.route('/history')
def event_history(): # Renamed function
    now = datetime.now()
    past_events = Event.query.filter(Event.event_time < now).order_by(Event.event_time.desc()).all() # Renamed variables
    return render_template('event_history.html', events=past_events) # Renamed template

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=5010, debug=True)