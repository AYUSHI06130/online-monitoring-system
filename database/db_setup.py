import sqlite3
import os

# ==========================================
# Create Database Folder
# ==========================================

os.makedirs("database", exist_ok=True)

DATABASE_PATH = "database/monitoring.db"

connection = sqlite3.connect(DATABASE_PATH)

cursor = connection.cursor()

# ==========================================
# Candidate Table
# ==========================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS Candidate(

    candidate_id TEXT PRIMARY KEY,

    name TEXT NOT NULL,

    email TEXT UNIQUE NOT NULL,

    password TEXT NOT NULL,

    photo_path TEXT

)
""")

# ==========================================
# Session Table
# ==========================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS Session(

    session_id INTEGER PRIMARY KEY AUTOINCREMENT,

    candidate_id TEXT NOT NULL,

    start_time TEXT,

    end_time TEXT,

    status TEXT,

    FOREIGN KEY(candidate_id)
    REFERENCES Candidate(candidate_id)

)
""")

# ==================================================
# Event Log Table
# ==================================================

cursor.execute("""

CREATE TABLE IF NOT EXISTS EventLog(

    event_id INTEGER PRIMARY KEY AUTOINCREMENT,

    candidate_id TEXT NOT NULL,

    event_type TEXT NOT NULL,

    timestamp TEXT NOT NULL,

    remarks TEXT,

    FOREIGN KEY(candidate_id)
    REFERENCES Candidate(candidate_id)

)

""")

print("===================================")
print("Database Created Successfully")
print("===================================")

connection.commit()

connection.close()


