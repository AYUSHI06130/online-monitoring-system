from flask import Blueprint, redirect, url_for, session, flash
import sqlite3
from datetime import datetime

from config import DATABASE

# ==========================================
# Blueprint
# ==========================================

exam = Blueprint("exam", __name__)


# ==========================================
# Helper Function
# Returns the latest session of the candidate
# ==========================================

def get_latest_session(candidate_id):

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    cursor.execute("""

    SELECT session_id, status

    FROM Session

    WHERE candidate_id=?

    ORDER BY session_id DESC

    LIMIT 1

    """, (candidate_id,))

    latest_session = cursor.fetchone()

    connection.close()

    return latest_session


# ==========================================
# Start Exam
# ==========================================

@exam.route("/start_exam")
def start_exam():

    if "candidate_id" not in session:

        flash("Please login first.")

        return redirect(url_for("auth.login"))

    candidate_id = session["candidate_id"]

    latest_session = get_latest_session(candidate_id)

    # If exam is already running
    if latest_session and latest_session[1] == "Running":

        flash("Exam is already running.")

        return redirect(url_for("auth.dashboard"))

    # If exam is paused
    if latest_session and latest_session[1] == "Paused":

        flash("Exam is paused. Please resume it instead.")

        return redirect(url_for("auth.dashboard"))

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    cursor.execute("""

    INSERT INTO Session
    (candidate_id, start_time, status)

    VALUES (?, ?, ?)

    """,

    (

        candidate_id,

        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),

        "Running"

    ))

    connection.commit()
    connection.close()

    flash("Exam Started Successfully.")

    return redirect(url_for("auth.dashboard"))


# ==========================================
# Pause Exam
# ==========================================

@exam.route("/pause_exam")
def pause_exam():

    if "candidate_id" not in session:

        flash("Please login first.")

        return redirect(url_for("auth.login"))

    candidate_id = session["candidate_id"]

    latest_session = get_latest_session(candidate_id)

    # No exam started
    if latest_session is None:

        flash("You have not started an exam yet.")

        return redirect(url_for("auth.dashboard"))

    # Already paused
    if latest_session[1] == "Paused":

        flash("Exam is already paused.")

        return redirect(url_for("auth.dashboard"))

    # Exam completed
    if latest_session[1] == "Completed":

        flash("Exam has already ended.")

        return redirect(url_for("auth.dashboard"))

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    cursor.execute("""

    UPDATE Session

    SET status=?

    WHERE session_id=?

    """,

    (

        "Paused",

        latest_session[0]

    ))

    connection.commit()
    connection.close()

    flash("Exam Paused Successfully.")

    return redirect(url_for("auth.dashboard"))


# ==========================================
# Resume Exam
# ==========================================

@exam.route("/resume_exam")
def resume_exam():

    if "candidate_id" not in session:

        flash("Please login first.")

        return redirect(url_for("auth.login"))

    candidate_id = session["candidate_id"]

    latest_session = get_latest_session(candidate_id)

    if latest_session is None:

        flash("You have not started an exam yet.")

        return redirect(url_for("auth.dashboard"))

    if latest_session[1] == "Running":

        flash("Exam is already running.")

        return redirect(url_for("auth.dashboard"))

    if latest_session[1] == "Completed":

        flash("Exam has already ended.")

        return redirect(url_for("auth.dashboard"))

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    cursor.execute("""

    UPDATE Session

    SET status=?

    WHERE session_id=?

    """,

    (

        "Running",

        latest_session[0]

    ))

    connection.commit()
    connection.close()

    flash("Exam Resumed Successfully.")

    return redirect(url_for("auth.dashboard"))


# ==========================================
# End Exam
# ==========================================

@exam.route("/end_exam")
def end_exam():

    if "candidate_id" not in session:

        flash("Please login first.")

        return redirect(url_for("auth.login"))

    candidate_id = session["candidate_id"]

    latest_session = get_latest_session(candidate_id)

    if latest_session is None:

        flash("You have not started an exam yet.")

        return redirect(url_for("auth.dashboard"))

    if latest_session[1] == "Paused":

        flash("Resume the exam before ending it.")

        return redirect(url_for("auth.dashboard"))

    if latest_session[1] == "Completed":

        flash("Exam has already ended.")

        return redirect(url_for("auth.dashboard"))

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    cursor.execute("""

    UPDATE Session

    SET

    end_time=?,

    status=?

    WHERE session_id=?

    """,

    (

        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),

        "Completed",

        latest_session[0]

    ))

    connection.commit()
    connection.close()

    flash("Exam Ended Successfully.")

    return redirect(url_for("auth.dashboard"))