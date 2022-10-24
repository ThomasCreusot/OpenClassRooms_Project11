from locust import HttpUser, task

club =  {
    "name":"Iron Temple", 
    "email": "admin@irontemple.com",
    "points":"4"
}

competition = {
    "name": "Spring Festival",
    "date": "2023-03-27 10:00:00",
    "numberOfPlaces": "25"
}

placesRequired = 1


class ProjectPerformanceTest(HttpUser):
    """An instantiation of HttpUser class represents an User"""

    @task
    def get_list_of_competitions(self):
        """The user (a club) logs on /showSummary and get a list of competitions"""

        self.client.post('/showSummary', data = club)

    @task
    def update_clubs_total_points(self):
        """The user (a club) logs on /purchasePlaces and books a place in a competition so the club
        points are updated"""

        data = {'competition': competition["name"],
        'club': club["name"],
        'places': placesRequired}

        self.client.post('/purchasePlaces', data=data)
