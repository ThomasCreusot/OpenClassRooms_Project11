import pytest
import server 

from server import app, MAX_CLUB_PLACES_PER_COMPETITION


A_KNOWN_CLUB = {
    "name":"A known club",
    "email":"test_club@mail.co",
    "points":"1"
}

FUTURE_COMPETITION = {
    "name": "Future competition",
    "date": "3000-12-31 00:00:00",
    "numberOfPlaces": "1"
}


@pytest.fixture
def client():  
    with app.test_client() as client:
        yield client


@pytest.fixture
def basic_competitions_fixture(monkeypatch):
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


@pytest.fixture
def basic_clubs_fixture(monkeypatch):
    test_clubs = [
        {
            "name":"A known club",
            "email":"test_club@mail.co",
            "points":"1"
        }, 
        {
            "name":"Another known club",
            "email":"test_other_club@mail.co",
            "points":"2"
        }
    ]
    monkeypatch.setattr(server, 'clubs', test_clubs)


def test_login_and_booking(client, basic_competitions_fixture, basic_clubs_fixture):
    """
    Tests the interaction between the following features:
      1. The secretary logs into the application.
      2. The secretary identifies an upcoming event and clicks on it.
        2.a. He/She sees the number of entries available and whether or not more can be accepted.
        2.b. He/She can then use the points accumulated to purchase tickets for the competition.
          2.b.i. If there are sufficient points and places available, he/she should see a
          confirmation message. The points used are then deducted from the club account.
          2.b.ii. They should receive an error message if the club does not have enough points, if
          they try to buy more than 12 places or if the competition is full.
        2.c. He/She can see the list of points of other clubs.
    """

    club = A_KNOWN_CLUB
    competition = FUTURE_COMPETITION
    placesRequired = 1

    # 1.Login
    response = client.get('/')
    assert response.status_code == 200

    response = client.post(
        "/showSummary", data=club
        )
    assert response.status_code == 200
    print("1. The secretary logs into the application.")


    # 2.1.Event identification and "click" --> Future competition get a 'Book Places' button
    # 2.1.1. Display number of available inscription(s)
    # 2.1.2. Display if new inscription are possible
    data = response.data.decode()
    assert data.find('            Future competition<br />' "\n"
                     '            Date: 3000-12-31 00:00:00</br>' "\n"
                     '            Number of Places: 1' "\n"
                     '            ' "\n"
                     '' "\n"
                     '                ' "\n"
                     '                <a href="/book/Future%20competition/A%20known%20club">Book Places</a>') != -1

    print("2. The secretary identifies an upcoming event ...")
    print("2.a. He/she sees the number of entries available and whether or not more can be accepted.")

    # 2.2 "Click" : model = http://127.0.0.1:5000/book/Spring%20Festival/Simply%20Lift
    response = client.get('/book/{0}/{1}'.format(competition['name'], club["name"]))
    assert response.status_code == 200
    print("2. The secretary identifies an upcoming event ... and clicks on it.")
    print("2.b. He/she can then use the points accumulated to purchase tickets for the competition.")


    # 3. Booking a place
    # 3.1. Enough competition places and club points: confirmation message and points deducted
    response = client.post("/purchasePlaces",
                   data = {'competition': competition["name"],
                           'club': club["name"],
                           'places': placesRequired}
    )
    assert response.status_code == 200

    data = response.data.decode()
    assert data.find('<li>Great-booking complete! You booked {0} place(s) for the competition {1}</li>'.format(placesRequired, competition['name'])) != -1
    print("2.b.i. If there are sufficient points and places available, he/she should see a confirmation message.")

    expected_club_points = int(club['points'])-placesRequired
    expected_competition_places = int(competition['numberOfPlaces'])-placesRequired
    assert data.find('Points available: {0}'.format(expected_club_points)) != -1
    assert data.find('Number of Places: {0}'.format(expected_competition_places)) != -1
    print("The points used are then deducted from the club account.")

    # 3.2. Not enough competition places or club points or more than 12 places : error message 
    response = client.post("/purchasePlaces",
                   data = {'competition': competition["name"],
                           'club': club["name"],
                           'places': placesRequired}
    )
    assert response.status_code == 200

    data = response.data.decode()
    assert data.find('You are neither allowed to book more than') != -1
    print("2.b.ii. They should receive an error message if the club does not have enough points, if they try to buy more than 12 places or if the competition is full.")


    # 4. A club can consult list of points of other clubs
    response = client.post(
        "/showSummary", data=club
        )

    data = response.data.decode()
    assert data.find("<h3>Clubs:</h3>") != -1
    assert data.find('            Another known club<br />' "\n"
                     '            Points: 2' "\n"
                     '        </li>' "\n") != -1

    print("2.c. He/she can see the list of points of other clubs.")