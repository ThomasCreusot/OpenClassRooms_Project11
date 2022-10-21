import server

from .conftest import client  # fixture import

from server import index, showSummary, book, purchasePlaces, logout
from server import MAX_CLUB_PLACES_PER_COMPETITION
from .conftest import basic_competitions_fixture, basic_clubs_fixture


FUTURE_COMPETITION = {
    "name": "Future competition",
    "date": "3000-12-31 00:00:00",
    "numberOfPlaces": "1"
}

PAST_COMPETITION = {
    "name": "Past competition",
    "date": "2000-01-01 00:00:00",
    "numberOfPlaces": "1"
}

INVALID_COMPETITION = {
    "name": "invalid Competition",
    "date": "2020-01-01 00:00:00",
    "numberOfPlaces": "0"
}

FUTURE_COMPETITION_WITH_MAX_CLUB_PLACES = {
    "name": "Future competition",
    "date": "3000-12-31 00:00:00",
    "numberOfPlaces": str(MAX_CLUB_PLACES_PER_COMPETITION * 2)
}

A_KNOWN_CLUB = {
    "name":"A known club",
    "email":"test_club@mail.co",
    "points":"1"
}

AN_UNKNOWN_CLUB = {
    "name":"An unknown club",
    "email":"facticeAdressNotInDatabase@mail.co",
    "points":"1"
}

A_CLUB_WITH_LESS_POINTS_THAN_MAX_CLUB_PLACES_PER_COMPETITION = {
    "name":"A club with less than MAX_CLUB_PLACES_PER_COMPETITION",
    "email":"test_club@mail.co",
    "points":"1"
}

A_CLUB_WITH_MORE_POINTS_THAN_MAX_CLUB_PLACES_PER_COMPETITION = {
    "name":"A club with more than MAX_CLUB_PLACES_PER_COMPETITION",
    "email": "admin@mail.com",
    # // conftest.py clubs_highNumberPoints_fixture
    "points": str(MAX_CLUB_PLACES_PER_COMPETITION + 2)
}


def test_index_should_status_code_be_200_and_return_data(client, basic_clubs_fixture):
    """Tests if index() returns a status code = 200 and expected data"""

    response = client.get('/')
    assert response.status_code == 200

    data = response.data.decode()
    # find() != -1 allows to know if the string is in data, independently of its position
    assert data.find("<h1>Welcome to the GUDLFT Registration Portal!</h1>") != -1
    assert data.find("Please enter your secretary email to continue:") != -1

    assert data.find("<h3>Clubs:</h3>") != -1
    assert data.find('<ul>' "\n"
                     '        ' "\n"
                     '        <li>' "\n"
                     '            A known club<br />' "\n"
                     '            Points: 1' "\n"
                     '        </li>' "\n") != -1


def test_showSummary_valid_known_email_should_status_code_200_and_return_data(client, basic_competitions_fixture, basic_clubs_fixture):
    """Tests if showSummary() returns a status code = 200 and expected data when email is known
    from the json database. Expected data differs between past competitions and futures
    competitions"""

    club = A_KNOWN_CLUB

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
                     '                <a href="/book/Future%20competition/A%20known%20club">Book Places</a>') != -1


def test_showSummary_valid_unknown_email_should_status_code_302(client, basic_clubs_fixture):
    """Tests if showSummary() returns a status code = 200 and expected data when email is not known
    from the json database."""

    club = AN_UNKNOWN_CLUB

    return_value = client.post(
        "/showSummary", data=club
        )
    assert return_value.status_code == 200

    data = return_value.data.decode()
    assert data.find('Unknown email adress') != -1


def test_book_should_status_code_200_and_return_data(client, basic_competitions_fixture, basic_clubs_fixture):
    """Tests if book() returns a status code = 200 and expected data when club and competition are
    known from the json database."""

    foundClub = A_KNOWN_CLUB
    foundCompetition = FUTURE_COMPETITION

    response = client.get('/book/{0}/{1}'.format(foundCompetition['name'], foundClub["name"]))
    assert response.status_code == 200

    data = response.data.decode()
    assert data.find('<input type="hidden" name="club" value="{0}">'.format(foundClub['name'])) != -1
    assert data.find('<input type="hidden" name="competition" value="{0}">'.format(foundCompetition['name'])) != -1


def test_book_invalid_club_should_status_code_200_and_return_data(client, basic_competitions_fixture, basic_clubs_fixture):
    """Tests if book() returns a status code = 200 and expected data when competition is known from
    the json database but club is not."""

    foundClub = AN_UNKNOWN_CLUB
    foundCompetition = FUTURE_COMPETITION

    response = client.get('/book/{0}/{1}'.format(foundCompetition['name'], foundClub["name"]))
    assert response.status_code == 500


def test_book_invalid_competition_should_status_code_200_and_return_data(client, basic_competitions_fixture, basic_clubs_fixture):
    """Tests if book() returns a status code = 200 and expected data when club is known from
    the json database but competition is not."""

    foundClub = A_KNOWN_CLUB
    foundCompetition = INVALID_COMPETITION

    response = client.get('/book/{0}/{1}'.format(foundCompetition['name'], foundClub["name"]))
    assert response.status_code == 500


def test_purchasePlaces_should_status_code_200_update_points_and_return_data(client, basic_competitions_fixture, basic_clubs_fixture):
    """Tests if purchasePlaces() returns a status code = 200 and expected data when club and
    competition are known from the database, and placesRequired is correct
    
    A correct placesRequired means : 
    placesRequired < MAX_CLUB_PLACES_PER_COMPETITION
    placesRequired <= club['points']
    """

    competition = FUTURE_COMPETITION
    club = A_KNOWN_CLUB
    placesRequired = 1

    return_value = client.post("/purchasePlaces",
                   data = {'competition': competition["name"],
                           'club': club["name"],
                           'places': placesRequired}
    )
    assert return_value.status_code == 200

    data = return_value.data.decode()
    assert data.find('<li>Great-booking complete! You booked {0} place(s) for the competition {1}</li>'.format(placesRequired, competition['name'])) != -1

    expected_club_points = int(club['points'])-placesRequired
    expected_competition_places = int(competition['numberOfPlaces'])-placesRequired
    assert data.find('Points available: {0}'.format(expected_club_points)) != -1
    assert data.find('Number of Places: {0}'.format(expected_competition_places)) != -1


def test_purchasePlaces_should_status_code_200_flash_too_much_placesRequired_one_booking(client, competitions_highNumberPoints_fixture, clubs_highNumberPoints_fixture):
    """Tests if purchasePlaces() returns a status code = 200 and expected data when club and
    competition are known from the database, but placesRequired is higher than 
    MAX_CLUB_PLACES_PER_COMPETITION"""

    competition = FUTURE_COMPETITION_WITH_MAX_CLUB_PLACES
    club = A_CLUB_WITH_MORE_POINTS_THAN_MAX_CLUB_PLACES_PER_COMPETITION
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


def test_purchasePlaces_should_status_code_200_flash_too_much_placesRequired_several_bookings(client, competitions_highNumberPoints_fixture, clubs_highNumberPoints_fixture):
    """Tests if purchasePlaces() returns a status code = 200 and expected data when club and
    competition are known from the database, placesRequired of several bookings are corrects but
    the sum of these placesRequired is higher than MAX_CLUB_PLACES_PER_COMPETITION"""

    competition = FUTURE_COMPETITION_WITH_MAX_CLUB_PLACES
    club = A_CLUB_WITH_MORE_POINTS_THAN_MAX_CLUB_PLACES_PER_COMPETITION

    # First booking
    placesRequired = MAX_CLUB_PLACES_PER_COMPETITION - 1
    first_booking_placesRequired = placesRequired
    for i in range(2):
        return_value = client.post("/purchasePlaces",
                    data = {'competition': competition["name"],
                            'club': club["name"],
                            'places': placesRequired}
        )
        if i == 0:
            # Second booking; total of spent points = MAX_CLUB_PLACES_PER_COMPETITION - 1 + 2
            placesRequired = 2

    assert return_value.status_code == 200

    data = return_value.data.decode()
    assert data.find('You are neither allowed to book more than') != -1

    expected_club_points = int(club['points']) - first_booking_placesRequired
    expected_competition_places = int(competition['numberOfPlaces']) - first_booking_placesRequired
    assert data.find('Points available: {0}'.format(expected_club_points)) != -1
    assert data.find('Number of Places: {0}'.format(expected_competition_places)) != -1

    assert data.find('<li>You already booked {0} places in competition {1} and asked {2} more.</li>'.format(
        MAX_CLUB_PLACES_PER_COMPETITION - 1, competition["name"], placesRequired))


def test_purchasePlaces_should_status_code_200_flash_too_less_club_points_compared_to_placesRequired(client, basic_competitions_fixture, clubs_lowNumberPoints_fixture):
    """Tests if purchasePlaces() returns a status code = 200 and expected data when club and
    competition are known from the database, but placesRequired is higher than club['points']"""

    competition = FUTURE_COMPETITION
    club = A_CLUB_WITH_LESS_POINTS_THAN_MAX_CLUB_PLACES_PER_COMPETITION
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


def test_purchasePlaces_should_status_code_200_flash_too_less_club_points_compared_to_competition(client, basic_competitions_fixture, clubs_highNumberPoints_fixture):
    """Tests if purchasePlaces() returns a status code = 200 and expected data when club and
    competition are known from the database, but placesRequired is higher than club['points']"""

    competition = FUTURE_COMPETITION
    club = A_CLUB_WITH_MORE_POINTS_THAN_MAX_CLUB_PLACES_PER_COMPETITION 
    placesRequired = int(competition["numberOfPlaces"]) + 1

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
