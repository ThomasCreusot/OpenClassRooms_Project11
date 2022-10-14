import pytest

from server import app

@pytest.fixture
def client():  
    # create_app({"TESTING": True})
    with app.test_client() as client:
        yield client