import sqlite3

DB_PATH = "winners.db"

def init_db():
    """
    Initializes the database connection and creates the 'winners' table if it does not exist.
    
    :return: Database connection object.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS winners (
            id TEXT PRIMARY KEY,
            email TEXT NOT NULL,
            state TEXT UNIQUE NOT NULL
        )
    """)
    conn.commit()
    return conn

def insert_or_update_winner(conn, winner):
    """
    Inserts a winner's information into the 'winners' table.
    If a winner from the same state already exists, it will be overwritten.
    
    :param conn: Database connection object.
    :param winner: Dictionary representing the winner with 'id', 'email', and 'state'.
    """
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO winners (id, email, state)
        VALUES (?, ?, ?)
        ON CONFLICT(state) DO UPDATE SET
            id=excluded.id,
            email=excluded.email
    """, (winner["id"], winner["email"], winner["state"]))
    conn.commit()

def get_winner_count(conn):
    """
    Retrieves the count of winners currently stored in the 'winners' table.
    
    :param conn: Database connection object.
    :return: Integer count of winners.
    """
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM winners")
    return cursor.fetchone()[0]

def get_all_winners(conn):
    """
    Retrieves all winners from the 'winners' table.
    
    :param conn: Database connection object.
    :return: List of tuples, where each tuple represents a winner (id, email, state).
    """
    cursor = conn.cursor()
    cursor.execute("SELECT id, email, state FROM winners")
    return cursor.fetchall()

def get_winner_by_id(conn, winner_id):
    """
    Checks if a winner with the given ID exists in the 'winners' table.
    If it does, it returns that winner.
    
    :param conn: Database connection object.
    :param winner_id: ID of the winner to check.
    :return: The winner's data if found, else None.
    """
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM winners WHERE id = ?", (winner_id,))
    return cursor.fetchone()
