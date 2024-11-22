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
    return render_template("index.html")


@app.route("/showSummary", methods=["POST"])
def showSummary():
    club = [club for club in clubs if club["email"] == request.form["email"]][0]
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


# TODO: Add route for points display


@app.route("/logout")
def logout():
    return redirect(url_for("index"))
