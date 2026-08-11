"""Flask application entry point for the student document portal."""

from flask import Flask, render_template


app = Flask(__name__)


@app.route("/")
def home():
    """Display the portal's public home page."""
    return render_template("home.html")


if __name__ == "__main__":
    app.run(debug=True)
