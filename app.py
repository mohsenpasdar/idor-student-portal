"""Flask application entry point for the student document portal."""

from functools import wraps
import os
import secrets

from flask import (
    Flask,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.security import check_password_hash

from database import get_user_by_id, get_user_by_username, init_app


app = Flask(__name__)
app.config.update(
    SECRET_KEY=os.environ.get("PORTAL_SECRET_KEY") or secrets.token_hex(32),
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
)
init_app(app)


@app.before_request
def load_logged_in_user():
    """Load the signed-in user from the session before each request."""
    user_id = session.get("user_id")

    if user_id is None:
        g.user = None
        return

    g.user = get_user_by_id(user_id)

    if g.user is None:
        session.clear()


def login_required(view):
    """Redirect anonymous visitors away from protected routes."""
    @wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("login"))

        return view(**kwargs)

    return wrapped_view


@app.route("/")
def home():
    """Display the portal's public home page."""
    return render_template("home.html")


@app.route("/login", methods=("GET", "POST"))
def login():
    """Authenticate a fictional student and create a signed session."""
    if g.user is not None:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = get_user_by_username(username)

        credentials_are_valid = user is not None and check_password_hash(
            user["password_hash"],
            password,
        )

        if not credentials_are_valid:
            flash("Incorrect username or password.", "error")
        else:
            session.clear()
            session["user_id"] = user["id"]
            return redirect(url_for("dashboard"))

    return render_template("login.html")


@app.route("/dashboard")
@login_required
def dashboard():
    """Display a protected placeholder for the document dashboard."""
    return render_template("dashboard.html")


@app.post("/logout")
def logout():
    """Remove all login information from the current session."""
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)
