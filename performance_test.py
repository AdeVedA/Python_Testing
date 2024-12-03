import random

from locust import HttpUser, between, task


class PerformanceTest(HttpUser):
    """
    Test de performance locust pour le site de competition à tester
    """

    wait_time = between(1, 5)  # Délai entre les requêtes des utilisateurs de 1 à 2 sec
    host = "http://localhost:5000"

    def on_start(self):
        self.client.post("/showSummary", data={"email": "john@simplylift.co"})

    @task(5)
    def index(self):
        """
        Accès à la page d'accueil.
        """
        self.client.get("/")

    @task(3)
    def view_points(self):
        self.client.get("/points")

    @task(3)
    def show_summary_get(self):
        """
        Connexion et chargement des compétitions.
        """
        with self.client.get("/showSummary", data={"club": "Simply Lift"}, catch_response=True) as response:
            if response.status_code == 500:
                response.failure(
                    "Unsuccessful return to showsummary with proper club name & points when redirecting from book"
                )
            else:
                response.success()

    @task(3)
    def book_competition(self):
        """
        simulation de la page de booking d'un club pour une competition (avec points et places et tableau de points)
        """
        competitions = ["Spring Festival", "Fall Classic", "Winter Superbowl"]
        clubs = ["Simply Lift", "Iron Temple", "She Lifts"]
        competition = random.choice(competitions)
        club = random.choice(clubs)
        with self.client.get(f"/book/{competition}/{club}", catch_response=True) as response:
            if response.status_code == 500:
                response.failure(f"Unsuccessful booking for the {competition} of {club}")
            else:
                response.success()

    @task(3)
    def purchase_places(self):
        """
        Simulation d'achat de places pour une compétition.
        """
        competitions = ["Spring Festival", "Fall Classic", "Winter Superbowl"]
        clubs = ["Simply Lift", "Iron Temple", "She Lifts"]
        competition = random.choice(competitions)
        club = random.choice(clubs)
        places = random.randint(1, 12)
        with self.client.post(
            "/purchasePlaces", data={"competition": competition, "club": club, "places": places}, catch_response=True
        ) as response:
            if response.status_code == 500:
                response.failure(f"Unsuccessful booking of {places} places for {club} on {competition}")
            else:
                response.success()

    @task(5)
    def logout(self):
        """
        simulation du logout
        """
        self.client.get("/logout")
