import logging
import time
from app.core import fetch_winners, handle_new_users
from app.core import MAX_RETRIES, TIME_INTERVAL, MAX_WINNERS
from app import db  # Import the db module

def main():
    current_winners = []

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
