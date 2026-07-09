import sqlite3
import os

# Database path
DATABASE_PATH = "database/monitoring.db"

# Create database folder if it doesn't exist
os.makedirs("database", exist_ok=True)

# Connect to SQLite database
connection = sqlite3.connect(DATABASE_PATH)

cursor = connection.cursor()

# ==================================================
# Candidate Table
# ==================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS Candidate (

    candidate_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    photo_path TEXT

)
""")

# ==================================================
# Session Table
# ==================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS Session (

    session_id INTEGER PRIMARY KEY AUTOINCREMENT,

    candidate_id TEXT NOT NULL,

    start_time TEXT NOT NULL,

    end_time TEXT,

    status TEXT NOT NULL,

    FOREIGN KEY(candidate_id)
    REFERENCES Candidate(candidate_id)

)
""")

# Save changes
connection.commit()

# Close connection
connection.close()

print("Database and Tables Created Successfully.")