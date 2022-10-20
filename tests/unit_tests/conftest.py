import pytest

import server 
from server import app, MAX_CLUB_PLACES_PER_COMPETITION


@pytest.fixture
def client():  
    # create_app({"TESTING": True})
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
        }
    ]
    monkeypatch.setattr(server, 'clubs', test_clubs)


@pytest.fixture
def clubs_highNumberPoints_fixture(monkeypatch):
    test_clubs = [
        {
            "name":"A club with more than MAX_CLUB_PLACES_PER_COMPETITION",
            "email": "admin@mail.com",
            "points":"1"
        }
    ]
    test_clubs[0]['points'] = str(MAX_CLUB_PLACES_PER_COMPETITION + 2)
    monkeypatch.setattr(server, 'clubs', test_clubs)


@pytest.fixture
def clubs_lowNumberPoints_fixture(monkeypatch):
    test_clubs = [
        {
            "name":"A club with less than MAX_CLUB_PLACES_PER_COMPETITION",
            "email":"test_club@mail.co",
            "points":"1"
        }
    ]
    monkeypatch.setattr(server, 'clubs', test_clubs)
