from .conftest import client  # import de la fixture

from server import index, showSummary, book, purchasePlaces, logout


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
def test_showSummary_valid_known_email_should_status_code_200_and_return_data(client):

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


def test_showSummary_valid_unknown_email_should_status_code_500(client):

    # TBD : mettre en place un mock ?
    club = {
        "name":"FacticeClubForTests",
        "email":"facticeAdressNotInDatabase@test.test",
        "points":"0"
    }

    return_value = client.post(
        "/showSummary", data=club
        )

    assert return_value.status_code == 500
    data = return_value.data.decode()
    assert data.find('The server encountered an internal error and was unable to complete your request. Either the server is overloaded or there is an error in the application.') != -1


