from server import loadClubs, loadCompetitions


# Tests d'Intégration
def test_full_booking_flow(client):
    """
    Test the complete booking flow
    Args:
        client: Flask test client
    """
    # Configuration initiale avec le club Simply Lift
    club = loadClubs()[0]
    competition = loadCompetitions()[0]
    initial_competition_places = int(competition["numberOfPlaces"])
    # Connexion
    login_response = client.post("/showSummary", data={"email": club["email"]})
    assert login_response.status_code == 200

    # Accès à la page de réservation
    booking_page = client.get(f'/book/{competition["name"]}/{club["name"]}')
    assert booking_page.status_code == 200

    # Réservation de 2 places
    purchase_response = client.post(
        "/purchasePlaces", data={"club": club["name"], "competition": competition["name"], "places": "2"}
    )
    assert purchase_response.status_code == 200
    assert b"Great, booking complete!" in purchase_response.data

    # récupérer la page de points pour les visualiser
    points_response = client.get("/points")
    assert points_response.status_code == 200

    # décoder le contenu html
    html_content = points_response.data.decode("utf-8")

    # vérifier que les points du club ont été mis-à-jour suite à la réservation
    expected_row = f"{club['name']}</td>\n                <td>{int(club['points']) - 2}</td>"
    assert expected_row in html_content

    # vérifier que les places de la compétition ont été mis à jour
    post_booking_competition_points = int(loadCompetitions()[0]["numberOfPlaces"])
    assert post_booking_competition_points == initial_competition_places - 2
    print(html_content)
