"""Flask application entry point for the student document portal."""

from functools import wraps
import os
import secrets

from flask import (
    Flask,
    abort,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.security import check_password_hash

from database import (
    get_document_by_id,
    get_document_by_id_and_owner,
    get_documents_by_owner,
    get_user_by_id,
    get_user_by_username,
    init_app,
)


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
    """Display only the documents owned by the signed-in student."""
    documents = get_documents_by_owner(g.user["id"])
    return render_template("dashboard.html", documents=documents)


@app.route("/document/vulnerable/<int:document_id>")
@login_required
def vulnerable_document(document_id):
    """Display a document without checking whether the user owns it."""
    document = get_document_by_id(document_id)

    if document is None:
        abort(404)

    # Intentionally vulnerable for this controlled experiment:
    # the route retrieves by document ID but does not compare owner_id with
    # g.user["id"]. The secure versions add that authorization step.
    owner = get_user_by_id(document["owner_id"])
    return render_template(
        "document.html",
        document=document,
        owner=owner,
        route_type="vulnerable",
    )


@app.route("/document/ownership-check/<int:document_id>")
@login_required
def ownership_check_document(document_id):
    """Display a document only when it belongs to the signed-in user."""
    document = get_document_by_id(document_id)

    if document is None:
        abort(404)

    # Defense 1: retrieve the requested object, then authorize access by
    # comparing its owner with the authenticated user from the session.
    if document["owner_id"] != g.user["id"]:
        abort(403)

    owner = get_user_by_id(document["owner_id"])
    return render_template(
        "document.html",
        document=document,
        owner=owner,
        route_type="ownership_check",
    )


@app.route("/document/scoped-query/<int:document_id>")
@login_required
def scoped_query_document(document_id):
    """Display a document only when its ID and owner match the current user."""
    # Defense 2: include the authenticated user ID in the database query so a
    # document owned by another user is not returned to the application.
    document = get_document_by_id_and_owner(document_id, g.user["id"])

    if document is None:
        abort(404)

    return render_template(
        "document.html",
        document=document,
        owner=g.user,
        route_type="scoped_query",
    )


@app.post("/logout")
def logout():
    """Remove all login information from the current session."""
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("home"))


@app.errorhandler(403)
@app.errorhandler(404)
def handle_http_error(error):
    """Display expected access and missing-page errors consistently."""
    messages = {
        403: (
            "Access forbidden",
            "You are signed in, but you are not allowed to access this resource.",
        ),
        404: (
            "Page not found",
            "The page or document you requested does not exist.",
        ),
    }
    error_title, error_message = messages[error.code]
    return (
        render_template(
            "error.html",
            status_code=error.code,
            error_title=error_title,
            error_message=error_message,
        ),
        error.code,
    )


if __name__ == "__main__":
    app.run(debug=True)
