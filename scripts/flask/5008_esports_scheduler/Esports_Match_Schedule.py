from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import re

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///c:/msBackups/DataBase/esports.db'
db = SQLAlchemy(app)

# Models
class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    logo_url = db.Column(db.String(300), nullable=False)

class Match(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    team1_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    team2_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    game_link = db.Column(db.String(300), nullable=False)
    game_time = db.Column(db.DateTime, nullable=False)

    team1 = db.relationship('Team', foreign_keys=[team1_id])
    team2 = db.relationship('Team', foreign_keys=[team2_id])

# Routes
@app.route('/')
def index():
    matches = Match.query.order_by(Match.game_time).all()
    return render_template('index.html', matches=matches)

from datetime import datetime, timedelta

@app.route('/add-match', methods=['GET', 'POST'])
def add_match():
    if request.method == 'POST':
        team1_id = request.form['team1']
        team2_id = request.form['team2']
        game_link = request.form['game_link']
        duration = request.form['duration']

        # Parse the duration
        days, hours, minutes = 0, 0, 0

        if 'd' in duration:
            days = int(duration.split('d')[0])
        if 'h' in duration:
            hours = int(duration.split('d')[-1].split('h')[0])
        if 'm' in duration:
            minutes = int(duration.split('h')[-1].split('m')[0])

        # Calculate match time (current time + duration)
        game_time = datetime.now() + timedelta(days=days, hours=hours, minutes=minutes)

        # Add match to the database
        match = Match(team1_id=team1_id, team2_id=team2_id, game_link=game_link, game_time=game_time)
        db.session.add(match)
        db.session.commit()
        return redirect(url_for('index'))

    # Sort teams alphabetically by name
    teams = Team.query.order_by(Team.name).all()
    return render_template('add_match.html', teams=teams)



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
    return render_template('teams.html', teams=teams)


@app.route('/delete-match/<int:id>', methods=['POST'])
def delete_match(id):
    match = Match.query.get_or_404(id)
    db.session.delete(match)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/delete-team/<int:id>', methods=['POST'])
def delete_team(id):
    team = Team.query.get_or_404(id)
    db.session.delete(team)
    db.session.commit()
    return redirect(url_for('manage_teams'))

@app.route('/edit-match/<int:match_id>', methods=['GET', 'POST'])
def edit_match(match_id):
    match = Match.query.get(match_id)
    teams = Team.query.order_by(Team.name).all()

    if request.method == 'POST':
        team1_id = request.form['team1']
        team2_id = request.form['team2']
        game_link = request.form['game_link']
        duration = request.form['duration']

        # Parse the duration
        days, hours, minutes = 0, 0, 0

        if 'd' in duration:
            days = int(duration.split('d')[0])
        if 'h' in duration:
            hours = int(duration.split('d')[-1].split('h')[0])
        if 'm' in duration:
            minutes = int(duration.split('h')[-1].split('m')[0])

        # Calculate match time (current time + duration)
        game_time = datetime.now() + timedelta(days=days, hours=hours, minutes=minutes)

        # Update the match details
        match.team1_id = team1_id
        match.team2_id = team2_id
        match.game_link = game_link
        match.game_time = game_time

        db.session.commit()
        return redirect(url_for('index'))

    return render_template('edit_match.html', match=match, teams=teams)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=5008, debug=True)


