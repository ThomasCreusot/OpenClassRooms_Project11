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
