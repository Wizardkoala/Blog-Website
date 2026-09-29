"""Flask blog post"""

from datetime import datetime
import os
import sqlite3
from contextlib import closing

from flask import Flask, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.config["DATABASE"] = os.path.join(app.instance_path, "users.sqlite3")
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY") or os.urandom(32)

os.makedirs(app.instance_path, exist_ok=True)


def init_db():
    """table stores information"""
    with closing(sqlite3.connect(app.config["DATABASE"])) as connection:
        connection.execute(
            "CREATE TABLE IF NOT EXISTS users "
            "(email TEXT PRIMARY KEY, password_hash TEXT NOT NULL)"
        )
        connection.commit()

def get_user(email):
    with closing(sqlite3.connect(app.config["DATABASE"])) as connection:
        connection.row_factory = sqlite3.Row
        return connection.execute(
            "SELECT email, password_hash FROM users WHERE email = ?", (email,)
        ).fetchone()


init_db()

#User registration/login
@app.route("/register", methods=["GET", "POST"])
def signup():
    """this is for the signup page"""
    if request.method == "POST":
        email = request.form.get("email", "")
        password = request.form.get("password", "")

        if not email or len(password) < 8:
            flash("Enter an e-mail and a password with at least 8 characters.")
            return render_template("register.html")

        try:
            with closing(sqlite3.connect(app.config["DATABASE"])) as connection:
                connection.execute(
                    "INSERT INTO users (email, password_hash) VALUES (?, ?)",
                    (email, generate_password_hash(password)),
                )
                connection.commit()
        except sqlite3.IntegrityError:
            flash("An account with that e-mail already exists.")
            return render_template("register.html")

        flash("Successfully registered!")
        return redirect(url_for("login"))
    return render_template("register.html")

#login page
@app.route('/login', methods=["GET", "POST"])
def login():
    """this is for the login page"""
    if request.method == "POST":
        email = request.form.get("email", "")
        password = request.form.get("password", "")
        user = get_user(email)

        if user is not None and check_password_hash(user["password_hash"], password):
            session["email"] = email
            return redirect(url_for("home"))
        flash("Incorrect E-mail or Password. Please try again.")
    return render_template("login.html")

@app.route("/logout", methods=["POST"])
def logout():
    """redirect for logout"""
    session.clear()
    return redirect(url_for("login"))

#home page
@app.route("/")
def home():
    """app route page"""
    if "email" not in session:
        return redirect(url_for("login"))
    return render_template("home.html")

@app.route('/profile')
def profile():
    if "email" not in session:
        flash("Please log in to view your profile.")
        return redirect(url_for("login"))
    return render_template('profile.html')

@app.route('/table')
def table():
    """Link for page to table"""
    current_time = datetime.now()
    return render_template('table.html', time_variable=current_time)

@app.route('/template')
def template():
    """Template html page"""
    return render_template('template.html')

if __name__ == "__main__":
    app.run(debug=True)
