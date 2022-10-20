import server

from .conftest import client  # import de la fixture

from server import index, showSummary, book, purchasePlaces, logout
from server import MAX_CLUB_PLACES_PER_COMPETITION

#index / Testez le code de réponse
def test_index_should_status_code_be_200(client):
    response = client.get('/')
    data = response.data.decode()

    assert response.status_code == 200
    # de ce que je comprends : find() est une fonction intégrée à Python qui permet de savoir si
    # la string  est dans data. Je pourrais écrire == 184, mais mon test ne passerait plus si on 
    # ajout quelque chose avant dans le fichier HTML. Pour simplement vérifier qu'il est présent, 
    # peu importe sa place, je mets != -1. S'il la string est absente, j'aurai un test qui ne passe
    # pas 
    assert data.find("<h1>Welcome to the GUDLFT Registration Portal!</h1>") != -1
    assert data.find("Please enter your secretary email to continue:") != -1


#showSummary / Testez le code de réponse et les données de réponse
def test_showSummary_valid_known_email_should_status_code_200_and_return_data(client, monkeypatch):

    test_competitions = [
        {
            "name": "Past competition",
            "date": "2000-01-01 00:00:00",
            "numberOfPlaces": "1"
        },
        {
            "name": "Future competition",
            "date": "3000-12-31 00:00:00",
            "numberOfPlaces": "1"
        }
    ]

    monkeypatch.setattr(server, 'competitions', test_competitions)

    # TBD : mettre en place un mock ?
    club = {
        "name":"Simply Lift",
        "email":"john@simplylift.co",
        "points":"13"
    }

    return_value = client.post(
        "/showSummary", data=club
        )

    assert return_value.status_code == 200
    data = return_value.data.decode()
    assert data.find('<h2>Welcome, {0} </h2><a href="/logout">Logout</a>'.format(club['email'])) != -1
    assert data.find('Points available: {0}'.format(club['points'])) != -1

    assert data.find('            Past competition<br />' "\n"
                     '            Date: 2000-01-01 00:00:00</br>' "\n"
                     '            Number of Places: 1' "\n"
                     '            ' "\n"
                     '' "\n"
                     '                ' "\n"
                     '                <a>Booking places is no more available</a>') != -1

    assert data.find('            Future competition<br />' "\n"
                     '            Date: 3000-12-31 00:00:00</br>' "\n"
                     '            Number of Places: 1' "\n"
                     '            ' "\n"
                     '' "\n"
                     '                ' "\n"
                     '                <a href="/book/Future%20competition/Simply%20Lift">Book Places</a>') != -1


def test_showSummary_valid_unknown_email_should_status_code_302(client):

    # TBD : mettre en place un mock ?
    club = {
        "name":"FacticeClubForTests",
        "email":"facticeAdressNotInDatabase@test.test",
        "points":"0"
    }

    return_value = client.post(
        "/showSummary", data=club
        )

    assert return_value.status_code == 200
    data = return_value.data.decode()
    assert data.find('Unknown email adress') != -1


def test_book_should_status_code_200_and_return_data(client):

    #mettre foundClub = qq chose, idem pour found competition ; vérifier la sortie. 
    #faire un autre test avec autres valeurs
    #renommer tests pour explicite.
    foundClub = {
        "name":"Simply Lift",
        "email":"john@simplylift.co",
        "points":"13"
    }

    foundCompetition = {
            "name": "Fall Classic",
            "date": "2020-10-22 13:30:00",
            "numberOfPlaces": "13"
        }

    response = client.get('/book/{0}/{1}'.format(foundCompetition['name'], foundClub["name"]))
    data = response.data.decode()
    assert response.status_code == 200
    assert data.find('<input type="hidden" name="club" value="{0}">'.format(foundClub['name'])) != -1
    assert data.find('<input type="hidden" name="competition" value="{0}">'.format(foundCompetition['name'])) != -1


def test_book_invalid_club_should_status_code_200_and_return_data(client):
    
    foundClub = {
        "name":"invalidClub",
        "email":"invalidClub@test.test",
        "points":"0"
    }

    foundCompetition = {
            "name": "Fall Classic",
            "date": "2020-10-22 13:30:00",
            "numberOfPlaces": "13"
        }
    response = client.get('/book/{0}/{1}'.format(foundCompetition['name'], foundClub["name"]))
    assert response.status_code == 500


def test_book_invalid_competition_should_status_code_200_and_return_data(client):

    foundClub = {
        "name":"Simply Lift",
        "email":"john@simplylift.co",
        "points":"13"
    }

    foundCompetition = {
            "name": "invalidCompetition",
            "date": "2020-10-22 13:30:00",
            "numberOfPlaces": "0"
        }
    response = client.get('/book/{0}/{1}'.format(foundCompetition['name'], foundClub["name"]))
    assert response.status_code == 500


#    if foundClub and foundCompetition:
#        return render_template('booking.html',club=foundClub,competition=foundCompetition)
#    else:
#        flash("Something went wrong-please try again")
#        return render_template('welcome.html', club=club, competitions=competitions)


def test_purchasePlaces_should_status_code_200_update_points_and_return_data(client):
    competition = {
            "name": "Spring Festival",
            "date": "2020-03-27 10:00:00",
            "numberOfPlaces": "25"
        }

    club = {
        "name":"Simply Lift",
        "email":"john@simplylift.co",
        "points":"13"
    }

    placesRequired = 1

    return_value = client.post("/purchasePlaces",
                   data = {'competition': competition["name"],
                           'club': club["name"],
                           'places': placesRequired}
    )


    assert return_value.status_code == 200
    data = return_value.data.decode()

    assert data.find('<li>Great-booking complete!</li>') != -1

    expected_club_points = int(club['points'])-placesRequired
    expected_competition_places = int(competition['numberOfPlaces'])-placesRequired
    assert data.find('Points available: {0}'.format(expected_club_points)) != -1
    assert data.find('Number of Places: {0}'.format(expected_competition_places)) != -1


def test_purchasePlaces_should_status_code_200_flash_too_much_placesRequired(client, monkeypatch):

    test_competitions = [
        {
            "name": "A competition",
            "date": "3000-01-01 00:00:00",
            "numberOfPlaces": "30"
        }]

    test_clubs = [
        {
            "name":"A club",
            "email": "admin@mail.com",
            "points":"4"
        }]

    monkeypatch.setattr(server, 'competitions', test_competitions)
    monkeypatch.setattr(server, 'clubs', test_clubs)


    competition = {
            "name": "A competition",
            "date": "3000-01-01 00:00:00",
            "numberOfPlaces": "30"
        }

    club = {
            "name":"A club",
            "email": "admin@mail.com",
            "points":"4"
    }

    placesRequired = MAX_CLUB_PLACES_PER_COMPETITION + 1

    return_value = client.post("/purchasePlaces",
                   data = {'competition': competition["name"],
                           'club': club["name"],
                           'places': placesRequired}
    )


    assert return_value.status_code == 200
    data = return_value.data.decode()

    assert data.find('You are neither allowed to book more than') != -1

    expected_club_points = int(club['points'])
    expected_competition_places = int(competition['numberOfPlaces'])
    assert data.find('Points available: {0}'.format(expected_club_points)) != -1
    assert data.find('Number of Places: {0}'.format(expected_competition_places)) != -1
    print(data)



def test_purchasePlaces_should_status_code_200_flash_too_less_club_points(client, monkeypatch):

    test_competitions = [
        {
            "name": "A competition",
            "date": "3000-01-01 00:00:00",
            "numberOfPlaces": "30"
        }]

    test_clubs = [
        {
            "name":"A club",
            "email": "admin@mail.com",
            "points":"4"
        }]

    monkeypatch.setattr(server, 'competitions', test_competitions)
    monkeypatch.setattr(server, 'clubs', test_clubs)


    competition = {
            "name": "A competition",
            "date": "3000-01-01 00:00:00",
            "numberOfPlaces": "30"
        }

    club = {
            "name":"A club",
            "email": "admin@mail.com",
            "points":"4"
    }

    placesRequired = int(club["points"]) + 1

    return_value = client.post("/purchasePlaces",
                   data = {'competition': competition["name"],
                           'club': club["name"],
                           'places': placesRequired}
    )


    assert return_value.status_code == 200
    data = return_value.data.decode()

    assert data.find('You are neither allowed to book more than') != -1

    expected_club_points = int(club['points'])
    expected_competition_places = int(competition['numberOfPlaces'])
    assert data.find('Points available: {0}'.format(expected_club_points)) != -1
    assert data.find('Number of Places: {0}'.format(expected_competition_places)) != -1
    print(data)