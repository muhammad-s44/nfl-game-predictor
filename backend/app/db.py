"""Opening the SQLite database for each API request.

FastAPI calls get_db() once per request (see Depends(get_db) in main.py):
the code before `yield` runs before the endpoint, the code after it runs
when the response is done, so every connection gets closed.
"""

import os
import sqlite3
from pathlib import Path

from fastapi import HTTPException

REPO = Path(__file__).resolve().parents[2]
DEFAULT_DB_PATH = REPO / "data" / "nfl.db"


def db_path():
    """Where the database lives. Tests point NFL_DB_PATH at a temporary copy."""
    return Path(os.environ.get("NFL_DB_PATH", DEFAULT_DB_PATH))


def get_db():
    path = db_path()
    if not path.exists():
        raise HTTPException(503, "Database not built yet. Run: python pipeline/build_db.py")
    # mode=ro opens the file read-only: the API can never change the data.
    # check_same_thread=False: FastAPI may open the connection on one worker
    # thread and run the endpoint on another. That is safe here because each
    # connection belongs to exactly one request.
    conn = sqlite3.connect(f"file:{path}?mode=ro", uri=True, check_same_thread=False)
    # Row lets us read columns by name (row["home_team"]) instead of position.
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()
