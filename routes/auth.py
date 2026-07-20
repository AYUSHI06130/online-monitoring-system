from flask import Blueprint, render_template, request
from flask import redirect, url_for
from flask import flash, session
from datetime import datetime

import sqlite3
import re

from config import DATABASE
from utils.camera import capture_photo

# ==========================================
# Blueprint
# ==========================================

auth = Blueprint("auth", __name__)

# ==========================================
# Candidate Registration
# ==========================================

@auth.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        candidate_id = request.form["candidate_id"].strip()
        name = request.form["name"].strip()
        email = request.form["email"].strip()
        password = request.form["password"].strip()

        # -----------------------------
        # Empty Field Validation
        # -----------------------------

        if candidate_id == "" or name == "" or email == "" or password == "":

            flash("All fields are required.")

            return redirect(url_for("auth.register"))

        # -----------------------------
        # Email Validation
        # -----------------------------

        email_pattern = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'

        if not re.match(email_pattern, email):

            flash("Invalid Email Format.")

            return redirect(url_for("auth.register"))

        # -----------------------------
        # Capture Photo
        # -----------------------------

        photo_path = capture_photo(candidate_id)

        if photo_path is None:

            flash("Photo Capture Cancelled.")

            return redirect(url_for("auth.register"))

        # -----------------------------
        # Database Connection
        # -----------------------------

        connection = sqlite3.connect(DATABASE)

        cursor = connection.cursor()

        # -----------------------------
        # Duplicate Email Check
        # -----------------------------

        cursor.execute(

            "SELECT * FROM Candidate WHERE email=?",

            (email,)

        )

        existing_user = cursor.fetchone()

        if existing_user:

            connection.close()

            flash("Email already registered.")

            return redirect(url_for("auth.register"))

        # -----------------------------
        # Insert Candidate
        # -----------------------------

        cursor.execute("""

        INSERT INTO Candidate
        VALUES(?,?,?,?,?)

        """,

        (

            candidate_id,
            name,
            email,
            password,
            photo_path

        ))

        connection.commit()

        connection.close()

        flash("Registration Successful!")

        return redirect(url_for("auth.login"))

    return render_template("register.html")


# ==========================================
# Candidate Login
# ==========================================

@auth.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"].strip()
        password = request.form["password"].strip()

        if email == "" or password == "":

            flash("Please fill all fields.")

            return redirect(url_for("auth.login"))

        connection = sqlite3.connect(DATABASE)

        cursor = connection.cursor()

        cursor.execute("""

        SELECT
            candidate_id,
            name,
            email

        FROM Candidate

        WHERE email=? AND password=?

        """,

        (

            email,
            password

        ))

        user = cursor.fetchone()

        if user:

            session["candidate_id"] = user[0]
            session["name"] = user[1]
            session["email"] = user[2]

            cursor.execute("""
            INSERT INTO EventLog
            (candidate_id,event_type,timestamp,remarks)
            VALUES(?,?,?,?)
            """,

            (
                session["candidate_id"],
                "Exam Started",
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Candidate Logged In"
            ))
            connection.commit()
            connection.close()

            flash("Login Successful!")

            return redirect(url_for("auth.dashboard"))

        else:

            flash("Invalid Email or Password.")

            return redirect(url_for("auth.login"))

    return render_template("login.html")


# ==========================================
# Dashboard
# ==========================================

@auth.route("/dashboard")
def dashboard():

    if "candidate_id" not in session:

        flash("Please login first.")

        return redirect(url_for("auth.login"))

    return render_template(

        "dashboard.html",

        candidate_id=session["candidate_id"],

        name=session["name"],

        email=session["email"]

    )


# ==========================================
# Logout
# ==========================================

@auth.route("/logout")
def logout():

    session.clear()

    flash("Logged Out Successfully.")

    return redirect(url_for("auth.login"))

