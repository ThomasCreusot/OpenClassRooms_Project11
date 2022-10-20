import server

from .conftest import client  # fixture import

from server import index, showSummary, book, purchasePlaces, logout
from server import MAX_CLUB_PLACES_PER_COMPETITION


def test_index_should_status_code_be_200_and_return_data(client):
    """Tests if index() returns a status code = 200 and expected data"""

    response = client.get('/')
    data = response.data.decode()

    assert response.status_code == 200
    # find() != -1 allows to know if the string is in data, independently of its position
    assert data.find("<h1>Welcome to the GUDLFT Registration Portal!</h1>") != -1
    assert data.find("Please enter your secretary email to continue:") != -1


def test_showSummary_valid_known_email_should_status_code_200_and_return_data(client, monkeypatch):
    """Tests if showSummary() returns a status code = 200 and expected data when email is known
    from the json database. Expected data differs between past competitions and futures
    competitions"""

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
    """Tests if showSummary() returns a status code = 200 and expected data when email is not known
    from the json database."""

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
    """Tests if book() returns a status code = 200 and expected data when club and competition are
    known from the json database."""

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
    """Tests if book() returns a status code = 200 and expected data when competition is known from
    the json database but club is not."""

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
    """Tests if book() returns a status code = 200 and expected data when club is known from
    the json database but competition is not."""

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


def test_purchasePlaces_should_status_code_200_update_points_and_return_data(client):
    """Tests if purchasePlaces() returns a status code = 200 and expected data when club and
    competition are known from the database, and placesRequired is correct
    
    A correct placesRequired means : 
    placesRequired < MAX_CLUB_PLACES_PER_COMPETITION
    placesRequired <= club['points']
    """

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


def test_purchasePlaces_should_status_code_200_flash_too_much_placesRequired_one_booking(client, monkeypatch):
    """Tests if purchasePlaces() returns a status code = 200 and expected data when club and
    competition are known from the database, but placesRequired is higher than 
    MAX_CLUB_PLACES_PER_COMPETITION"""

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


def test_purchasePlaces_should_status_code_200_flash_too_much_placesRequired_several_bookings(client, monkeypatch):
    """Tests if purchasePlaces() returns a status code = 200 and expected data when club and
    competition are known from the database, placesRequired of several bookings are corrects but
    the sum of these placesRequired is higher than MAX_CLUB_PLACES_PER_COMPETITION"""

    test_competitions = [
        {
            "name": "A competition",
            "date": "3000-01-01 00:00:00",
            "numberOfPlaces": "30"
        }]

    # Note : The club got enough points to try more than 12 bookings
    test_clubs = [
        {
            "name":"A club",
            "email": "admin@mail.com",
            "points":"20"
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
            "points":"20"
    }

    # First booking
    placesRequired = MAX_CLUB_PLACES_PER_COMPETITION - 1
    first_booking_placesRequired = placesRequired

    return_value = client.post("/purchasePlaces",
                   data = {'competition': competition["name"],
                           'club': club["name"],
                           'places': placesRequired}
    )

    # Second booking; total of spent points = MAX_CLUB_PLACES_PER_COMPETITION - 1 + 2
    placesRequired = 2

    return_value = client.post("/purchasePlaces",
                   data = {'competition': competition["name"],
                           'club': club["name"],
                           'places': placesRequired}
    )


    assert return_value.status_code == 200
    data = return_value.data.decode()

    assert data.find('You are neither allowed to book more than') != -1

    expected_club_points = int(club['points']) - first_booking_placesRequired
    expected_competition_places = int(competition['numberOfPlaces']) - first_booking_placesRequired
    assert data.find('Points available: {0}'.format(expected_club_points)) != -1
    assert data.find('Number of Places: {0}'.format(expected_competition_places)) != -1
    assert data.find('<li>You already booked {0} places in competition {1} and asked {2} more.</li>'.format(
        MAX_CLUB_PLACES_PER_COMPETITION - 1,
        competition["name"],
        placesRequired
    ))


def test_purchasePlaces_should_status_code_200_flash_too_less_club_points(client, monkeypatch):
    """Tests if purchasePlaces() returns a status code = 200 and expected data when club and
    competition are known from the database, but placesRequired is higher than club['points']"""

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
