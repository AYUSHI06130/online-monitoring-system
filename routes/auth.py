from flask import Blueprint, render_template, request
from flask import redirect, url_for
from flask import flash, session

import sqlite3
import re
from datetime import datetime
from utils.camera import capture_photo

from config import DATABASE

# Create Blueprint
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

        # ----------------------------
        # Validation
        # ----------------------------

        if candidate_id == "" or name == "" or email == "" or password == "":

            flash("All fields are required.")

            return redirect(url_for("auth.register"))

        # ----------------------------
        # Email Validation
        # ----------------------------

        email_pattern = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'

        if not re.match(email_pattern, email):

            flash("Invalid Email Format.")

            return redirect(url_for("auth.register"))

        # ----------------------------
        # Capture Candidate Photo
        # ----------------------------

        photo_path = capture_photo(candidate_id)
        print("Returned from capture_photo()")
        print(photo_path)

        if photo_path is None:

            flash("Photo capture cancelled.")

            return redirect(url_for("auth.register"))

        # ----------------------------
        # Database Connection
        # ----------------------------

        connection = sqlite3.connect(DATABASE)

        cursor = connection.cursor()

        # ----------------------------
        # Duplicate Email Check
        # ----------------------------

        cursor.execute(

            "SELECT * FROM Candidate WHERE email=?",

            (email,)

        )

        existing_user = cursor.fetchone()

        if existing_user:

            connection.close()

            flash("Email already registered.")

            return redirect(url_for("auth.register"))

        # ----------------------------
        # Insert Candidate
        # ----------------------------
        print("About to insert into database")
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
        print("Database committed")

        flash("Registration Successful.")

        return redirect(url_for("auth.login"))

    return render_template("register.html")

# ==========================================
# Candidate Login
# ==========================================

@auth.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        # -------------------------
        # Get Login Data
        # -------------------------

        email = request.form["email"].strip()
        password = request.form["password"].strip()

        # -------------------------
        # Empty Field Validation
        # -------------------------

        if email == "" or password == "":

            flash("Please fill all fields.")

            return redirect(url_for("auth.login"))

        # -------------------------
        # Connect to Database
        # -------------------------

        connection = sqlite3.connect(DATABASE)

        cursor = connection.cursor()

        # -------------------------
        # Check Login Credentials
        # -------------------------

        cursor.execute("""

        SELECT candidate_id, name, email

        FROM Candidate

        WHERE email=? AND password=?

        """,

        (

            email,
            password

        ))

        user = cursor.fetchone()

        connection.close()

        # -------------------------
        # Login Successful
        # -------------------------

        if user:

            session["candidate_id"] = user[0]
            session["name"] = user[1]
            session["email"] = user[2]

            flash("Login Successful!")

            return redirect(url_for("auth.dashboard"))

        # -------------------------
        # Login Failed
        # -------------------------

        else:

            flash("Invalid Email or Password.")

            return redirect(url_for("auth.login"))

    return render_template("login.html")

# ==========================================
# Dashboard
# ==========================================

@auth.route("/dashboard")
def dashboard():

    if "name" not in session:

        return redirect(url_for("auth.login"))

    return render_template(

        "dashboard.html",

        name=session["name"],

        email=session["email"]

    )


# ==========================================
# Logout
# ==========================================

@auth.route("/logout")
def logout():

    connection = sqlite3.connect(DATABASE)

    cursor = connection.cursor()

    cursor.execute("""

    UPDATE Session

    SET

    end_time=?,
    status=?

    WHERE

    candidate_id=?
    AND
    status='Active'

    """,

    (

        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Completed",
        session["candidate_id"]

    ))

    connection.commit()

    connection.close()

    session.clear()

    flash("Logged out successfully.")

    return redirect(url_for("auth.login"))