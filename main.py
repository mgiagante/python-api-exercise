import logging
import time
import requests
import db  # Import the db module

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

def validate_user(user):
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

    # Check if the user already exists by ID
    existing_winner = db.get_winner_by_id(conn, winner["id"])
    
    if existing_winner:
        logging.info(f"Skipped winner with existing ID: {winner['id']}")
        return  # Do nothing if the user already exists by ID
    
    # If no conflict by ID, proceed to insert (overwritting if same state).
    db.insert_or_update_winner(conn, winner)

def handle_new_users(data, conn):
    """
    Processes a batch of users, validates them and persists them. 
    
    :param data: List of users as dictionaries.
    :param conn: Database connection object.
    """

    for user in data:
        if validate_user(user):
            winner = {
                "id": user["id"],
                "email": user["email"],
                "state": user["address"]["state"]
            }

            count = db.get_winner_count(conn)

            # Ensure we don't exceed MAX_WINNERS
            if count < MAX_WINNERS:
                add_winner(conn, winner)
                logging.info(f"Inserted/Updated winner: {winner}")
            else:
                logging.info(f"Skipped winner: {winner} (would exceed MAX_WINNERS)")
        else:
            logging.info(f"Invalid user skipped: {user}")

def main():
    conn = db.init_db()
    retries = 0

    while True:
        if retries >= MAX_RETRIES:
            logging.error("API unavailable after max retries. Exiting.")
            break

        data = fetch_winners()
        if not data:
            retries += 1
            time.sleep(TIME_INTERVAL)
            continue

        retries = 0  # Reset retries on success
        handle_new_users(data, conn)

        # Check if MAX_WINNERS was reached. 
        count = db.get_winner_count(conn)
        logging.info(f"Winner Count: {count}")

        if count == MAX_WINNERS:
            logging.info("Lottery complete. Final winners:")
            winners = db.get_all_winners(conn)

            for winner in winners:
                logging.info(winner)

            break
        else:
            time.sleep(TIME_INTERVAL)

if __name__ == "__main__":
    main()
