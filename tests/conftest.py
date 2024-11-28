import pytest

from server import app


# Fixtures - Configuration des tests
@pytest.fixture
def client():
    """
    Fixture that configures Flask application for testing
    Returns:
        FlaskClient: Flask test client to simulate HTTP requests
    """
    # Configuration de l'app en mode test
    app.config["TESTING"] = True
    # Création d'un client de test
    with app.test_client() as client:
        yield client


@pytest.fixture
def mock_clubs():
    """
    Fixture that provides clubs data for testing
    Returns:
        dict: Test clubs data
    """
    return {
        "clubs": [
            {"name": "Simply Lift", "email": "john@simplylift.co", "points": "13"},
            {"name": "Iron Temple", "email": "admin@irontemple.com", "points": "4"},
            {"name": "She Lifts", "email": "kate@shelifts.co.uk", "points": "12"},
        ]
    }


@pytest.fixture
def mock_competitions():
    """
    Fixture that provides competitions data for testing
    Returns:
        dict: Test competitions data
    """
    return {
        "competitions": [
            {"name": "Spring Festival", "date": "2024-12-27 10:00:00", "numberOfPlaces": "25"},
            {"name": "Fall Classic", "date": "2024-12-22 13:30:00", "numberOfPlaces": "13"},
        ]
    }
