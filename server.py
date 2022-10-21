import json

from datetime import datetime

from flask import Flask,render_template,request,redirect,flash,url_for


MAX_CLUB_PLACES_PER_COMPETITION = 12


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


def get_authorisation_to_reserve_places(club, competition, placesRequired):
    if 'reserved_competitions' in club:
        # Club already reserved (a) place(s) at least in a competition
        if competition["name"] in club["reserved_competitions"]:
            if placesRequired <= MAX_CLUB_PLACES_PER_COMPETITION - club["reserved_competitions"][competition["name"]]:
                # Club already reserved for this competition : dict update
                return True
            else: 
                return False
        else:
            # Club already reserved but not for this competition : dict creation
            if placesRequired <= MAX_CLUB_PLACES_PER_COMPETITION:
                club["reserved_competitions"][competition["name"]] = 0  # will be updated; first version : = placesRequired
                return True
            else:
                return False
    else:
        # Club never reserved places for any : dict creation
        club["reserved_competitions"] = {}
        if placesRequired <= MAX_CLUB_PLACES_PER_COMPETITION:
            club["reserved_competitions"][competition["name"]] = 0 # will be updated; first version : = placesRequired
            return True
        else:
            return False


def update_authorisation_to_reserve_places(club, competition, placesRequired):
    club["reserved_competitions"][competition["name"]] += placesRequired


def get_enough_points_to_reserve_places(club, placesRequired):
    if int(club['points']) >= placesRequired:
        return True
    else:
        return False


def known_adress_or_not(emailFromForm):
    known_adress = False
    for a_club in clubs:
        if a_club['email'] == emailFromForm:
            known_adress = True
        else:
            pass
    return known_adress


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/showSummary',methods=['POST'])
def showSummary():
    known_adress = known_adress_or_not(request.form['email'])

    if known_adress == True : 
        club = [club for club in clubs if club['email'] == request.form['email']][0]
        competition_date_validity(competitions)
        return render_template('welcome.html',club=club,competitions=competitions, clubs=clubs)
    else: 
        flash("Unknown email adress")
        return render_template('index.html')


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

    authorisation_to_reserve_places = get_authorisation_to_reserve_places(club, competition, placesRequired)
    enough_points_to_reserve_places = get_enough_points_to_reserve_places(club, placesRequired)

    if authorisation_to_reserve_places == True and enough_points_to_reserve_places == True and placesRequired <= int(competition['numberOfPlaces']):

        update_authorisation_to_reserve_places(club, competition, placesRequired)
        competition['numberOfPlaces'] = int(competition['numberOfPlaces'])-placesRequired
        club['points'] = int(club['points'])-placesRequired
        flash('Great-booking complete!')

        competition_date_validity(competitions)

    else:
        flash('You are neither allowed to book more than 12 places for a competition, nor allowed to spend more points than you have on your account ({0}) and you are not allowed to book more places than available in the concerned competition.'.format(club['points']))
        if 'reserved_competitions' in club:
            if competition["name"] in club["reserved_competitions"]:
                flash('You already booked {0} places in competition {1} and asked {2} more.'.format(
                    club["reserved_competitions"][competition["name"]],
                    competition["name"],
                    placesRequired))


    print(club)
    return render_template('welcome.html', club=club, competitions=competitions, clubs=clubs)


# TODO: Add route for points display


@app.route('/logout')
def logout():
    return redirect(url_for('index'))