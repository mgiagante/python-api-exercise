import logging
import requests
from app import db  # Import the db module

API_URL = "https://random-data-api.com/api/users/random_user?size=5"
API_TIMEOUT = 5 
MAX_RETRIES = 3

TIME_INTERVAL = 10 
MAX_WINNERS = 25

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")

def fetch_winners():
    """
    Fetches a batch of users from the API.

    :return: List of users or None if the API request fails.
    """
    try:
        logging.info("Making request to fetch winners.")
        response = requests.get(API_URL, timeout=API_TIMEOUT)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logging.error(f"API request failed: {e}")
        return None

def is_valid(user):
    """
    Validates if a user has the required fields to be eligible as a winner.

    :param user: Dictionary representing a user.
    :return: True if the user is valid, False otherwise.
    """
    try:
        if user.get("address"):
            return all([
                user.get("id"),
                user.get("email"),
                user["address"].get("state")
            ])
        return False
    except KeyError:
        return False

def add_winner(conn, winner):
    """
    Adds a new winner to the database.
    If a winner with the same ID already exists, it does nothing.
    
    :param conn: Database connection object.
    :param winner: Dictionary representing a winner.
    """

    if winner_already_exists(conn, winner):
        logging.info(f"Skipped winner with existing ID: {winner['id']}")
        return  # Do nothing if a user with that ID already exists.
    
    # If no conflict by ID, proceed to insert (overwritting if same state).
    db.insert_or_update_winner(conn, winner)

def winner_already_exists(conn, winner):
    """
    :param conn: Database connection object.
    :param winner: Dictionary representing a winner.

    :return: True if the winner exists in the database, False otherwise.
    """

    return bool(db.get_winner_by_id(conn, winner["id"]))

def handle_new_users(data, conn):
    """
    Processes a batch of users, validates them and persists them. 
    
    :param data: List of users as dictionaries.
    :param conn: Database connection object.
    """

    for user in data:
        if is_valid(user):
            winner = winner_from(user)
            count = db.get_winner_count(conn)

            # Ensure we don't exceed MAX_WINNERS.
            if count < MAX_WINNERS:
                add_winner(conn, winner)
                logging.info(f"Inserted/Updated winner: {winner}")
            else:
                logging.info(f"Skipped winner: {winner} (would exceed MAX_WINNERS)")
        else:
            logging.info(f"Invalid user skipped: {user}")

def winner_from(user):
    """
    Parses the fields needed from the user coming from the API response into
    a reduced winner dictionary object.
    """
    return {
        "id": user["id"],
        "email": user["email"],
        "state": user["address"]["state"]
    }
    
