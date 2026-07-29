from flask import Blueprint, render_template, redirect, url_for
from flask import send_from_directory
from flask import flash, session
from flask import request,jsonify,session
from flask import Response
import cv2

from utils.camera_manager import CameraManager
from utils.integrity_score import calculate_integrity_score

import sqlite3
from datetime import datetime



from config import DATABASE

# ==========================================
# Blueprint
# ==========================================

exam = Blueprint("exam", __name__)

# ==========================================
# Camera Manager
# ==========================================

camera_manager = None


# ==========================================
# Helper Function
# ==========================================

def get_latest_session(candidate_id):

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    cursor.execute("""

    SELECT
        session_id,
        status

    FROM Session

    WHERE candidate_id=?

    ORDER BY session_id DESC

    LIMIT 1

    """, (candidate_id,))

    latest = cursor.fetchone()

    connection.close()

    return latest

# ==========================================
# Video Frame Generator
# ==========================================

def generate_frames():

    global camera_manager

    if camera_manager is None:
        return

    while True:

        latest = get_latest_session(camera_manager.candidate_id)

        if latest is None:
            break

        # Stop streaming only after exam has ended

        if latest[1] == "Ended":
            break

        frame = camera_manager.get_frame()

        if frame is None:
            break

        success, buffer = cv2.imencode(".jpg", frame)

        if not success:
            continue

        frame_bytes = buffer.tobytes()

        yield (
            b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n'
            + frame_bytes +
            b'\r\n'
        )

    camera_manager.stop_camera()

# ==========================================
# Video Feed
# ==========================================

@exam.route("/video_feed")
def video_feed():

    return Response(

        generate_frames(),

        mimetype="multipart/x-mixed-replace; boundary=frame"

    )

# ==========================================
# Exam Page
# ==========================================

@exam.route("/exam")
def exam_page():

    if "candidate_id" not in session:

        flash("Please login first.")

        return redirect(url_for("auth.login"))

    latest = get_latest_session(session["candidate_id"])

    status = "Not Started"

    if latest:

        status = latest[1]

    return render_template(
    "exam.html",
    status=status,
    exam_ended=(status == "Ended"),
    name=session["name"],
    candidate_id=session["candidate_id"]
    )

    


# ==========================================
# Start Exam
# ==========================================

@exam.route("/start_exam")
def start_exam():
    print("========== START EXAM ROUTE CALLED ==========")

    if "candidate_id" not in session:

        flash("Please login first.")

        return redirect(url_for("auth.login"))

    candidate_id = session["candidate_id"]

    #new update---------
    global camera_manager

    camera_manager = CameraManager(candidate_id)
    print("CameraManager created")

    opened = camera_manager.start_camera()

    print("Camera opened:", opened)

    if not opened:

        flash("Unable to access webcam.")

        return redirect(url_for("exam.exam_page"))
    #---------------------    

    latest = get_latest_session(candidate_id)

    # --------------------------------------

    if latest:

        if latest[1] == "Running":

            flash("Exam is already running.")

            return redirect(url_for("exam.exam_page"))

        if latest[1] == "Paused":

            flash("Resume the exam instead of starting again.")

            return redirect(url_for("exam.exam_page"))

    # --------------------------------------

    connection = sqlite3.connect(DATABASE)

    cursor = connection.cursor()

    cursor.execute("""

    INSERT INTO Session

    (candidate_id,start_time,status)

    VALUES(?,?,?)

    """,

    (

        candidate_id,

        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),

        "Running"

    ))

    connection.commit()

    # Save the Session table record
    connection.commit()

    # Get the newly created session_id
    session_id = cursor.lastrowid

    # Log Exam Started event
    cursor.execute("""
    INSERT INTO EventLog
    (
        candidate_id,
        session_id,
        event_type,
        timestamp,
        remarks
    )
    VALUES (?, ?, ?, ?, ?)
    """,
    (
        candidate_id,
        session_id,
        "Exam Started",
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Candidate started the exam"
    ))

    connection.commit()
    connection.close()

    flash("Exam started successfully")

    return redirect(url_for("exam.exam_page"))

# ==========================================
# Log Browser Activity
# ==========================================

@exam.route("/log_browser_event", methods=["POST"])
def log_browser_event():

    candidate_id = session.get("candidate_id")
    

    if candidate_id is None:
        return jsonify({"status": "error"}), 401

    latest = get_latest_session(candidate_id)

    if latest is None:
        return jsonify({"status": "error", "message": "No active session"}), 400

    session_id = latest[0]    

    data = request.get_json()

    event_type = data["event_type"]
    remarks = data["remarks"]

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO EventLog
        (
            candidate_id,
            session_id,
            event_type,
            timestamp,
            remarks
        )

        VALUES (?, ?, ?, ?,?)
    """,
    (
        candidate_id,
        session_id,
        event_type,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        remarks
    ))

    connection.commit()
    connection.close()

    return jsonify({"status": "success"}) 


# ==========================================
# Pause / Resume
# ==========================================

@exam.route("/toggle_exam")
def toggle_exam():

    if "candidate_id" not in session:

        flash("Please login first.")
        return redirect(url_for("auth.login"))

    latest = get_latest_session(session["candidate_id"])

    if latest is None:

        flash("Start the exam first.")
        return redirect(url_for("exam.exam_page"))

    session_id = latest[0]
    status = latest[1]

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    # ==========================================
    # Pause Exam
    # ==========================================

    if status == "Running":

        cursor.execute("""

            UPDATE Session

            SET
                status=?,
                paused_at=?

            WHERE session_id=?

        """,

        (

            "Paused",
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            session_id

        ))

        flash("Exam Paused Successfully.")

    # ==========================================
    # Resume Exam
    # ==========================================

    elif status == "Paused":

        cursor.execute("""

            SELECT
                paused_at,
                total_pause_seconds

            FROM Session

            WHERE session_id=?

        """,

        (

            session_id,

        ))

        data = cursor.fetchone()

        paused_at = data[0]
        total_pause = data[1]

        paused_time = datetime.strptime(
            paused_at,
            "%Y-%m-%d %H:%M:%S"
        )

        pause_duration = int(
            (datetime.now() - paused_time).total_seconds()
        )

        total_pause += pause_duration

        cursor.execute("""

            UPDATE Session

            SET
                status=?,
                paused_at=NULL,
                total_pause_seconds=?

            WHERE session_id=?

        """,

        (

            "Running",
            total_pause,
            session_id

        ))

        flash("Exam Resumed Successfully.")

    # ==========================================
    # Already Ended
    # ==========================================

    elif status == "Ended":

        flash("Exam has already ended.")
        connection.close()

        return redirect(url_for("exam.exam_page"))

    connection.commit()
    connection.close()

    return jsonify({"status": "success"})


# ==========================================
# End Exam
# ==========================================

@exam.route("/end_exam")
def end_exam():

    if "candidate_id" not in session:

        flash("Please login first.")

        return redirect(url_for("auth.login"))

    latest = get_latest_session(session["candidate_id"])

    if latest is None:

        flash("Start the exam first.")

        return redirect(url_for("exam.exam_page"))

    session_id = latest[0]

    status = latest[1]

    if status == "Ended":

        flash("Exam already ended.")

        return redirect(url_for("exam.exam_page"))

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

        "Ended",

        session_id

    ))

    connection.commit()

    connection.close()

    # ------------------------------------
    # Calculate Integrity Score
    # ------------------------------------

    candidate_id = session["candidate_id"]

    result = calculate_integrity_score(
        candidate_id,
        session_id
    )

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM EventLog
        WHERE candidate_id=?
        AND session_id=?
        AND event_type='Face Not Detected'
    """, (session["candidate_id"], session_id))

    face_absence_count = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM EventLog
        WHERE candidate_id=?
        AND session_id=?
        AND event_type='Browser Focus Lost'
    """, (session["candidate_id"], session_id))

    browser_loss_count = cursor.fetchone()[0]

    # Total Suspicious Events
    cursor.execute("""
    SELECT COUNT(*)
    FROM EventLog
    WHERE candidate_id=?
    AND session_id=?
    """,
    (
        candidate_id,
        session_id
    ))

    total_events = cursor.fetchone()[0]

    connection.close()
    global camera_manager

    if camera_manager is not None:

        camera_manager.stop_camera()

        camera_manager = None

    flash("Exam Ended Successfully.")

    return render_template(
        "result.html",
        score=result["score"],
        risk=result["risk"],
        face_absence_count=face_absence_count,
        browser_loss_count=browser_loss_count,
        total_events=total_events
    )

# ==========================================
# Get Monitoring Status
# ==========================================

@exam.route("/get_monitoring_status")
def get_monitoring_status():

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    # ----------------------------------
    # Monitoring Status
    # ----------------------------------

    cursor.execute("""

        SELECT
            face_status,
            face_absence_count

        FROM MonitoringStatus

        WHERE candidate_id=?

    """,

    (

        session["candidate_id"],

    ))

    monitoring = cursor.fetchone()

    # ----------------------------------
    # Current Session
    # ----------------------------------

    cursor.execute("""

        SELECT
            start_time,
            status,
            paused_at,
            total_pause_seconds

        FROM Session

        WHERE candidate_id=?

        ORDER BY session_id DESC

        LIMIT 1

    """,

    (

        session["candidate_id"],

    ))

    exam = cursor.fetchone()

    connection.close()

    # ----------------------------------
    # Face Status
    # ----------------------------------

    if monitoring:

        face_status = monitoring[0]
        face_absence_count = monitoring[1]

    else:

        face_status = "Unknown"
        face_absence_count = 0

    # ----------------------------------
    # Timer Calculation
    # ----------------------------------

    session_status = "Not Started"
    elapsed_seconds = 0

    if exam:

        start_time = datetime.strptime(
            exam[0],
            "%Y-%m-%d %H:%M:%S"
        )

        session_status = exam[1]

        paused_at = exam[2]

        total_pause_seconds = exam[3] or 0

        # --------------------------
        # Running
        # --------------------------

        if session_status == "Running":

            elapsed_seconds = int(

                (datetime.now() - start_time).total_seconds()

            ) - total_pause_seconds

        # --------------------------
        # Paused
        # --------------------------

        elif session_status == "Paused":

            pause_time = datetime.strptime(

                paused_at,

                "%Y-%m-%d %H:%M:%S"

            )

            elapsed_seconds = int(

                (pause_time - start_time).total_seconds()

            ) - total_pause_seconds

        # --------------------------
        # Ended
        # --------------------------

        elif session_status == "Ended":

            cursor = sqlite3.connect(DATABASE).cursor()

            connection = sqlite3.connect(DATABASE)

            cursor = connection.cursor()

            cursor.execute("""

                SELECT end_time

                FROM Session

                WHERE candidate_id=?

                ORDER BY session_id DESC

                LIMIT 1

            """,

            (

                session["candidate_id"],

            ))

            end = cursor.fetchone()

            connection.close()

            if end and end[0]:

                end_time = datetime.strptime(

                    end[0],

                    "%Y-%m-%d %H:%M:%S"

                )

                elapsed_seconds = int(

                    (end_time - start_time).total_seconds()

                ) - total_pause_seconds

    return jsonify({

        "face_status": face_status,
        "face_absence_count": face_absence_count,
        "session_status": session_status,
        "elapsed_seconds": max(elapsed_seconds, 0)

    })

@exam.route("/scores")
def view_scores():

    connection = sqlite3.connect(DATABASE)

    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    cursor.execute("""

        SELECT *

        FROM IntegrityScore

        ORDER BY calculated_at DESC

    """)

    scores = cursor.fetchall()

    connection.close()

    return render_template(
        "scores.html",
        scores=scores
    )    