import json
from datetime import datetime

from flask import Flask, flash, redirect, render_template, request, url_for


def loadClubs():
    """get the list of clubs from the JSON clubs file
    Returns:
        listOfClubs (list) or empty list
    """
    try:
        with open("clubs.json", "r") as c:
            listOfClubs = json.load(c)["clubs"]  # Chargement du contenu JSON
            return listOfClubs
    except FileNotFoundError:
        flash("Error: clubs.json file not found.")
        return []  # Retourner une liste vide pour éviter les plantages
    except json.JSONDecodeError:
        flash("Error: Failed to decode clubs.json.")
        return []


def loadCompetitions():
    """get the list of competitions from a JSON competitions file
    Returns:
        listOfCompetitions (list) or empty list
    """
    try:
        with open("competitions.json", "r") as comps:
            listOfCompetitions = json.load(comps)["competitions"]
            return listOfCompetitions
    except FileNotFoundError:
        flash("Error: competitions.json file not found.")
        return []
    except json.JSONDecodeError:
        flash("Error: Failed to decode competitions.json.")
        return []


def save_data_to_json(file_path, data):
    """Save updated data to a JSON file.
    Args:
        file_path (str): Path to the JSON file.
        data (dict): Data to save.
    """
    try:
        with open(file_path, "w") as file:
            json.dump(data, file, indent=4)
    except Exception as e:
        print(f"Error saving data to {file_path}: {e}")


app = Flask(__name__)
app.secret_key = "something_special"

competitions = loadCompetitions()
clubs = loadClubs()


@app.route("/")
def index():
    """renders home root index page"""
    return render_template("index.html")


@app.route("/showSummary", methods=["POST"])
def showSummary():
    """renders welcome page with competitions' datas list and logged-in club's points"""
    email = request.form.get("email")
    if not email:
        flash("Email is required.")
        return redirect(url_for("index"))

    club = next((club for club in clubs if club["email"] == email), None)  # Trouver le club correspondant
    if not club:
        flash("Club not found.")
        return redirect(url_for("index"))

    return render_template("welcome.html", club=club, competitions=competitions)


@app.route("/book/<competition>/<club>")
def book(competition, club):
    """render a pager for a club to book for a specific future competition"""
    foundClub = next((c for c in clubs if c["name"] == club), None)
    foundCompetition = next((c for c in competitions if c["name"] == competition), None)
    current_date = datetime.now()
    competition_date = datetime.strptime(foundCompetition["date"], "%Y-%m-%d %H:%M:%S")

    if competition_date < current_date:
        flash("trying to book places for a past competition is not allowed")
        return render_template("welcome.html", club=club, competitions=competitions)

    if not foundClub or not foundCompetition:
        flash("Invalid club or competition.")
        return redirect(url_for("index"))

    return render_template("booking.html", club=foundClub, competition=foundCompetition, clubs=clubs)


@app.route("/purchasePlaces", methods=["POST"])
def purchasePlaces():
    """permits places'booking for a competition"""
    competition_name = request.form.get("competition")
    club_name = request.form.get("club")
    placesRequired = request.form.get("places")

    if not competition_name or not club_name or not placesRequired:
        flash("Missing data for booking.")
        return redirect(url_for("index"))

    try:
        placesRequired = int(placesRequired)
    except ValueError:
        flash("Invalid number of places.")
        return redirect(url_for("index"))

    # utilisation de next() pour ne trouver de manière efficiente qu'un élément,
    # et gérer le cas d'erreur où l'élément n'est pas trouvé (retourne "None")
    competition = next((c for c in competitions if c["name"] == competition_name), None)
    club = next((c for c in clubs if c["name"] == club_name), None)
    club_points = int(club["points"])

    if not competition or not club:
        flash("Invalid club or competition.")
        return redirect(url_for("index"))

    if placesRequired <= 0:
        flash("booking 0 or less places is quite surprising, please book a significant number of places")
        return render_template("welcome.html", club=club, competitions=competitions)
    if placesRequired > 12:
        flash("booking more than 12 places is not allowed")
        return render_template("welcome.html", club=club, competitions=competitions)
    if placesRequired > int(competition["numberOfPlaces"]):
        flash("Not enough places available. Try to respect the number of places available.")
        return render_template("welcome.html", club=club, competitions=competitions)
    if placesRequired > club_points:
        flash("Not enough club points available. Try to respect the limits of your available points for booking.")
        return render_template("welcome.html", club=club, competitions=competitions)

    competition["numberOfPlaces"] = int(competition["numberOfPlaces"]) - placesRequired
    club["points"] = club_points - placesRequired

    # Save updated data to JSON files
    try:
        save_data_to_json("competitions.json", {"competitions": competitions})
        save_data_to_json("clubs.json", {"clubs": clubs})
        flash("Great, booking complete!")
    except Exception as e:
        flash("An error occurred while saving data. Please try again.")
        print(f"Error: {e}")

    return render_template("welcome.html", club=club, competitions=competitions)


@app.route("/points")
def points_display():
    """
    Display the points for all clubs in a tabular format.
    Uses loadClubs to ensure clubs data is loaded freshly and handles errors.
    """
    try:
        # Charger les clubs avec gestion des erreurs
        refreshed_clubs = loadClubs()  # Rafraîchit les données des clubs depuis le fichier
        if not refreshed_clubs:
            flash("No club data available to display points.")
            return redirect(url_for("index"))  # Rediriger vers l'accueil en cas d'erreur

        # Calcul et préparation des données pour le tableau
        clubs_with_points = [{"name": club["name"], "points": club.get("points", 0)} for club in refreshed_clubs]

        # Rendre le template pour afficher les points
        return render_template("points.html", clubs=clubs_with_points)

    except Exception as e:
        # Gestion d'erreurs imprévues
        print(f"Unexpected error in points_display: {e}")
        flash("An error occurred while displaying points.")
        return redirect(url_for("index"))


@app.route("/logout")
def logout():
    """log out and get back to index page"""
    return redirect(url_for("index"))
