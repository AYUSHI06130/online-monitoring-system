import sqlite3
from datetime import datetime
from config import DATABASE

# Penalty for each suspicious event
PENALTIES = {
    "Face Not Detected": 5,
    "Browser Focus Lost": 10,
    "Browser Tab Changed": 10,
    "Long Face Absence": 15,
    "Multiple Face Absence": 20,
    "Camera Blocked": 15,
    "Multiple Faces Detected": 20
}


def calculate_integrity_score(candidate_id, session_id):

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT event_type
        FROM EventLog
        WHERE candidate_id = ?
        AND session_id = ?
    """, (candidate_id,session_id))

    events = cursor.fetchall()


    # Face absence count
    cursor.execute("""
    SELECT face_absence_count
    FROM MonitoringStatus
    WHERE candidate_id=?
    """, (candidate_id,))

    row = cursor.fetchone()

    face_absence_count = row[0] if row else 0

    cursor.execute("""
    SELECT COUNT(*)
    FROM EventLog
    WHERE candidate_id=?
    AND session_id=?
    AND event_type='Browser Focus Lost'
    """, (candidate_id, session_id))

    browser_loss_count = cursor.fetchone()[0]

    score = 100

    for event in events:

        event_name = event[0]

        if event_name in PENALTIES:
            score -= PENALTIES[event_name]

    score = max(score, 0)

    total_events = len(events)

    if score >= 90:
        risk = "Excellent"

    elif score >= 75:
        risk = "Low Risk"

    elif score >= 50:
        risk = "Medium Risk"

    elif score >= 25:
        risk = "High Risk"

    else:
        risk = "Very High Risk"

    cursor.execute("""
        INSERT INTO IntegrityScore
        (
            candidate_id,
            session_id,
            final_score,
            risk_level,
            total_events,
            calculated_at
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """,
    (
        candidate_id,
        session_id,
        score,
        risk,
        total_events,
        datetime.now()
    ))

    conn.commit()
    conn.close()

    return {
        "score": score,
        "risk": risk,
        "face_absence_count": face_absence_count,
        "browser_loss_count": browser_loss_count,
        "total_events": total_events
    }