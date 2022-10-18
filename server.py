import json

from datetime import datetime

from flask import Flask,render_template,request,redirect,flash,url_for


def loadClubs():
    with open('clubs.json') as c:
         listOfClubs = json.load(c)['clubs']
         return listOfClubs


def loadCompetitions():
    with open('competitions.json') as comps:
         listOfCompetitions = json.load(comps)['competitions']
         return listOfCompetitions


app = Flask(__name__)
app.secret_key = 'something_special'

competitions = loadCompetitions()
clubs = loadClubs()

def competition_date_validity(competitions):
    """Determines for each competition if it is valid or not, based on its date"""
    for competition in competitions:
        now = datetime.now(tz=None)
        competition_time = datetime.strptime(competition["date"], "%Y-%m-%d %H:%M:%S")
        if competition_time > now:
            competition["date_validity"]=True
        elif competition_time <= now:
            competition["date_validity"]=False


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/showSummary',methods=['POST'])
def showSummary():
    club = [club for club in clubs if club['email'] == request.form['email']][0]
    competition_date_validity(competitions)
    return render_template('welcome.html',club=club,competitions=competitions, clubs=clubs)


@app.route('/book/<competition>/<club>')
def book(competition,club):
    foundClub = [c for c in clubs if c['name'] == club][0]
    foundCompetition = [c for c in competitions if c['name'] == competition][0]
    if foundClub and foundCompetition:
        return render_template('booking.html',club=foundClub,competition=foundCompetition)
    else:
        flash("Something went wrong-please try again")
        competition_date_validity(competitions)
        return render_template('welcome.html', club=club, competitions=competitions, clubs=clubs)


@app.route('/purchasePlaces',methods=['POST'])
def purchasePlaces():
    competition = [c for c in competitions if c['name'] == request.form['competition']][0]
    club = [c for c in clubs if c['name'] == request.form['club']][0]
    placesRequired = int(request.form['places'])
    competition['numberOfPlaces'] = int(competition['numberOfPlaces'])-placesRequired
    club['points'] = int(club['points'])-placesRequired
    flash('Great-booking complete!')

    competition_date_validity(competitions)

    return render_template('welcome.html', club=club, competitions=competitions, clubs=clubs)


# TODO: Add route for points display


@app.route('/logout')
def logout():
    return redirect(url_for('index'))