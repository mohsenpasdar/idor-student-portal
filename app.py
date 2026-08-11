"""Flask application entry point for the student document portal."""

from flask import Flask, render_template

from database import get_documents_by_owner, get_user_by_username, init_app


app = Flask(__name__)
init_app(app)


@app.route("/")
def home():
    """Display the portal's public home page."""
    alice = get_user_by_username("alice")
    alice_documents = get_documents_by_owner(alice["id"]) if alice else []

    database_ready = alice is not None and len(alice_documents) == 2
    return render_template("home.html", database_ready=database_ready)


if __name__ == "__main__":
    app.run(debug=True)
