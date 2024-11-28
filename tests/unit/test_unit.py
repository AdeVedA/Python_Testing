import json

from server import app, loadClubs, loadCompetitions, save_data_to_json

# == Tests Unitaires ==


# Tests des fonctions utilitaires
def test_loadClubs_success(mocker):
    """
    Test successful clubs loading
    Args:
        mocker: pytest-mock fixture
    """
    # Simulation d'un fichier JSON valide
    mock_open = mocker.mock_open(read_data='{"clubs": [{"name": "Test Club"}]}')
    mocker.patch("builtins.open", mock_open)

    result = loadClubs()
    assert len(result) == 1
    assert result[0]["name"] == "Test Club"


def test_loadClubs_file_not_found(mocker):
    """
    Test clubs loading with missing file
    """
    # Simulation d'un FileNotFoundError
    mocker.patch("server.json.load", side_effect=FileNotFoundError)

    # Mock de flash pour vérifier son utilisation
    mock_flash = mocker.patch("server.flash")

    # Appeler la fonction
    result = loadClubs()

    assert result == []
    mock_flash.assert_called_once_with("Error: clubs.json file not found.")


def test_loadClubs_json_decode_error(client, mocker):
    # Mock de json.load pour lever une JSONDecodeError
    mocker.patch("server.json.load", side_effect=json.JSONDecodeError("msg", "doc", 0))

    # Mock de flash pour vérifier son utilisation
    mock_flash = mocker.patch("server.flash")

    result = loadClubs()

    assert result == []  # La fonction doit retourner une liste vide
    mock_flash.assert_called_once_with("Error: Failed to decode clubs.json.")


def test_loadCompetitions_success(mocker):
    """
    Test successful competitions loading
    """
    # Simulation d'un fichier JSON valide
    mock_json_data = '{"competitions": [{"name": "Spring Festival", "date": "2024-12-27", "numberOfPlaces": "25"}]}'
    mock_open = mocker.mock_open(read_data=mock_json_data)
    mocker.patch("builtins.open", mock_open)

    result = loadCompetitions()
    assert len(result) == 1
    assert result[0]["name"] == "Spring Festival"
    assert result[0]["date"] == "2024-12-27"
    assert result[0]["numberOfPlaces"] == "25"


def test_loadCompetitions_file_not_found(mocker):
    """
    Test competitions loading with missing file
    """
    # Simulation d'un filenotfounderror
    mocker.patch("builtins.open", side_effect=FileNotFoundError)

    with app.test_request_context():
        result = loadCompetitions()
        assert result == []


def test_loadCompetitions_json_decode_error(mocker):
    # Mock de json.load pour lever une JSONDecodeError
    mocker.patch("server.json.load", side_effect=json.JSONDecodeError("msg", "doc", 0))

    # Mock de flash pour vérifier son utilisation
    mock_flash = mocker.patch("server.flash")

    result = loadCompetitions()

    assert result == []  # La fonction doit retourner une liste vide
    mock_flash.assert_called_once_with("Error: Failed to decode competitions.json.")


def test_save_data_to_json_success(mocker, tmp_path):
    # chemin temporaire pour le fichier de test
    file_path = tmp_path / "test.json"

    # Les données à écrire dans le fichier
    test_data = {"key": "value"}

    # Appeler la fonction
    save_data_to_json(file_path, test_data)

    # Vérifier que le fichier a bien été créé
    assert file_path.exists()

    # Charger et vérifier le contenu du fichier
    with open(file_path, "r") as f:
        saved_data = json.load(f)
    assert saved_data == test_data


def test_save_data_to_json_error(mocker):
    # Mock `open` pour qu'il lève une exception
    mock_open = mocker.patch("builtins.open", side_effect=IOError("Cannot write to file"))

    # Mock `print` pour capturer les messages d'erreur
    mock_print = mocker.patch("builtins.print")

    # Appeler la fonction avec un chemin invalide
    save_data_to_json("invalid/path/test.json", {"key": "value"})

    # Vérifier que `open` a été appelé avec les bons arguments
    mock_open.assert_called_once_with("invalid/path/test.json", "w")

    # Vérifier que le message d'erreur a été affiché
    mock_print.assert_called_once_with("Error saving data to invalid/path/test.json: Cannot write to file")


# test de == index ==
def test_index(client):
    """
    Test the home page
    Args:
        client: Flask test client fixture
    """
    # Envoi d'une requête GET à la racine
    response = client.get("/")
    # Vérification que la réponse est OK (200)
    assert response.status_code == 200
    # Vérification qu'une partie unique du contenu attendu est présent dans la réponse
    assert b"Welcome to the" in response.data


# tests de == showSummary ==
def test_showSummary_valid_email(client, mocker):
    """
    Test login with valid email
    Args:
        mocker: pytest-mock fixture for function simulation
    """
    # Simulation du chargement des clubs
    mocker.patch("server.clubs", [{"name": "Simply Lift", "email": "john@simplylift.co", "points": "13"}])

    # Simulation d'une connexion
    response = client.post("/showSummary", data={"email": "john@simplylift.co"})

    # Vérifications
    assert response.status_code == 200
    assert b"Welcome, john@simplylift.co" in response.data


def test_show_summary_post_missing_email(client):
    """Test: POST /showSummary avec email manquant."""
    response = client.post("/showSummary", data={}, follow_redirects=True)
    assert b"Email is required." in response.data
    assert response.status_code == 200  # Redirection attendue.


def test_show_summary_post_invalid_email(client, mocker):
    """Test: POST /showSummary avec email invalide."""
    mocker.patch("server.loadClubs", return_value=[{"email": "valid@example.com"}])
    response = client.post("/showSummary", data={"email": "invalid@example.com"}, follow_redirects=True)
    assert b"Club not found." in response.data
    assert response.status_code == 200


def test_show_summary_get_missing_club(client):
    """Test: GET /showSummary avec nom de club manquant."""
    response = client.get("/showSummary", follow_redirects=True)
    assert b"Club information is missing." in response.data
    assert response.status_code == 200


def test_show_summary_get_invalid_club(client, mocker):
    """Test: GET /showSummary avec club invalide."""
    mocker.patch("server.loadClubs", return_value=[{"name": "Club XForce"}])
    response = client.get("/showSummary", query_string={"club": "Invalid Club"}, follow_redirects=True)
    assert b"Club not found." in response.data
    assert response.status_code == 200


# tests de == book ==
def test_book_valid_competition(client, mocker):
    """
    Test booking a valid competition
    """
    # Configuration des données de test
    club = {"name": "Simply Lift", "email": "john@simplylift.co", "points": "13"}
    competition = {"name": "Spring Festival", "date": "2024-12-27 10:00:00", "numberOfPlaces": "25"}

    # Mock des données
    mocker.patch("server.clubs", [club])
    mocker.patch("server.competitions", [competition])

    # Test de la page de réservation
    response = client.get(f'/book/{competition["name"]}/{club["name"]}')

    assert response.status_code == 200
    assert b"Spring Festival" in response.data


def test_book_invalid_competition_or_club(client, mocker):
    """Test: /book avec compétition ou club invalide."""
    mocker.patch("server.loadClubs", return_value=[{"name": "Club XForce"}])
    mocker.patch("server.loadCompetitions", return_value=[{"name": "Competition Strength"}])
    response = client.get("/book/Invalid Competition/Invalid Club", follow_redirects=True)
    assert b"Invalid club or competition." in response.data
    assert response.status_code == 200


def test_book_past_competition(client, mocker):
    """Test: /book pour une compétition passée."""
    mocker.patch("server.clubs", [{"name": "Club XForce"}])
    mocker.patch(
        "server.competitions",
        [{"name": "Competition Strength", "date": "1969-06-20 00:00:00", "numberOfPlaces": "25"}],
    )
    response = client.get("/book/Competition Strength/Club XForce", follow_redirects=True)
    assert b"trying to book places for a past competition is not allowed" in response.data
    assert response.status_code == 200


# tests de == purchasePlaces ==
def test_purchase_places_valid(client, mocker):
    """Test valid place purchase"""
    club = {"name": "Simply Lift", "email": "john@simplylift.co", "points": "13"}
    competition = {"name": "Spring Festival", "date": "2024-12-27 10:00:00", "numberOfPlaces": "25"}

    mocker.patch("server.clubs", [club])
    mocker.patch("server.competitions", [competition])
    mocker.patch("server.save_data_to_json")
    response = client.post(
        "/purchasePlaces", data={"club": club["name"], "competition": competition["name"], "places": "2"}
    )

    assert response.status_code == 200
    assert b"Great, booking complete!" in response.data


def test_purchase_places_missing_data(client):
    """Test: POST /purchasePlaces with missing data"""
    response = client.post("/purchasePlaces", data={}, follow_redirects=True)
    assert b"Missing data for booking." in response.data
    assert response.status_code == 200


def test_purchase_places_invalid_places(client, mocker):
    """Test: POST /purchasePlaces with an invalid (string) number of places"""
    mocker.patch("server.loadClubs", return_value=[{"name": "Club XForce", "points": "10"}])
    mocker.patch("server.loadCompetitions", return_value=[{"name": "Competition Strength", "numberOfPlaces": "5"}])
    mocker.patch("server.save_data_to_json")
    # cas où la demande incorpore une valeur invalide (par exmeple une string)
    response = client.post(
        "/purchasePlaces",
        data={"competition": "Competition Strength", "club": "Club XForce", "places": "blabla"},
        follow_redirects=True,
    )
    assert b"Invalid number of places." in response.data
    assert response.status_code == 200


def test_purchase_places_invalid_club_or_competition(client, mocker):
    """Test: POST /purchasePlaces trying to book more than available places."""
    mocker.patch("server.clubs", [])
    mocker.patch("server.competitions", [])

    # Cas où la demande dépasse les places disponibles
    response = client.post(
        "/purchasePlaces",
        data={"competition": "Competition Strength", "club": "Club XForce", "places": "6"},
        follow_redirects=True,
    )
    assert b"Invalid club or competition." in response.data
    assert response.status_code == 200


def test_purchase_places_negative_place_required(client, mocker):
    """Test: POST /purchasePlaces trying to book a negative number of places."""
    mocker.patch("server.clubs", [{"name": "Club XForce", "points": "10"}])
    mocker.patch("server.competitions", [{"name": "Competition Strength", "numberOfPlaces": "5"}])

    # Cas où la demande dépasse les places disponibles
    response = client.post(
        "/purchasePlaces",
        data={"competition": "Competition Strength", "club": "Club XForce", "places": "-6"},
        follow_redirects=True,
    )
    assert b"booking 0 or less places is quite surprising" in response.data
    assert response.status_code == 200


def test_purchase_places_exceed_allowed_booking(client, mocker):
    """Test: POST /purchasePlaces trying to book more than allowed number of places for booking"""
    mocker.patch("server.clubs", [{"name": "Club XForce", "points": "20"}])
    mocker.patch("server.competitions", [{"name": "Competition Strength", "numberOfPlaces": "20"}])

    # Cas où la demande dépasse le nombres de places max autorisées
    response = client.post(
        "/purchasePlaces",
        data={"competition": "Competition Strength", "club": "Club XForce", "places": "15"},
        follow_redirects=True,
    )
    assert b"booking more than 12 places is not allowed" in response.data
    assert response.status_code == 200


def test_purchase_places_exceed_available_places(client, mocker):
    """Test: POST /purchasePlaces trying to book more than available places."""
    mocker.patch("server.clubs", [{"name": "Club XForce", "points": "10"}])
    mocker.patch("server.competitions", [{"name": "Competition Strength", "numberOfPlaces": "5"}])

    # Cas où la demande dépasse les places disponibles
    response = client.post(
        "/purchasePlaces",
        data={"competition": "Competition Strength", "club": "Club XForce", "places": "6"},
        follow_redirects=True,
    )
    assert b"Not enough places available." in response.data
    assert response.status_code == 200


def test_purchase_places_exceed_club_points(client, mocker):
    """Test: POST /purchasePlaces trying to book places without enough club points"""
    mocker.patch("server.clubs", [{"name": "Club XForce", "points": "5"}])
    mocker.patch("server.competitions", [{"name": "Competition Strength", "numberOfPlaces": "10"}])

    # Cas où la demande dépasse les points du club
    response = client.post(
        "/purchasePlaces",
        data={"competition": "Competition Strength", "club": "Club XForce", "places": "6"},
        follow_redirects=True,
    )
    assert b"Not enough club points available." in response.data

    assert response.status_code == 200


# test de == points_display ==
def test_points_display_success(client, mocker):
    """Test: POST /purchasePlaces with an invalid (string) number of places"""
    mocker.patch("server.loadClubs", return_value=[{"name": "Club XForce", "points": "10"}])

    response = client.get(
        "/points",
        data={"club": "Club XForce"},
        follow_redirects=True,
    )
    assert b"Club XForce" in response.data
    assert response.status_code == 200


def test_points_display_no_clubs(client, mocker):
    """Test: POST /purchasePlaces with an invalid (string) number of places"""
    mocker.patch("server.loadClubs", return_value=[])

    response = client.get(
        "/points",
        data={},
        follow_redirects=True,
    )
    assert b"No club data available to display points." in response.data
    assert response.status_code == 200


def test_logout_follow_redirect(client):
    response = client.get("/logout", follow_redirects=True)

    assert response.status_code == 200
    assert b"Please enter your secretary email to continue:" in response.data
