# python-api-exercise

This Python script implements a lottery system that queries an API to select 25 unique winners, one from each U.S. state.
The winners are stored in a SQLite database, and the script handles API failures and winner replacement for the same state.

## Features
- Polls an API every 10 seconds to fetch random users.
- Ensures only one winner per state is stored in the database.
- Logs all updates and displays the final winners' list.
- Uses SQLite as the database, with no external dependencies for setup.

## Schema
- The data schema for winners is (id, email, state) with state as a unique constraint to simplify winner replacement.

## Unit Tests
- Parsing API responses.
- Database insertion and winner replacement logic.

## Invariants
- Ensure that every state's winner is unique, hence only one per state exists in the database table when the script is finished.

## Error Handling
- If the API is unavailable, skip the iteration since another one will happen 10 seconds after that.
- If the API is unavailable for an extended period (e.g., more than MAX_RETRIES attempts), exit the script with an error message. This is to avoid infinite loops in production.

## Running the Script

1. Install dependencies locally:
```bash
pip install -r requirements.txt
```

2. Run the tests:
```bash
pytest tests/*
```
3. Run the script
```bash
python3 main.py
```
