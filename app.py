import os
import secrets
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from pathlib import Path
from urllib.parse import quote

from dash import Dash
from flask import Flask, flash, has_request_context, redirect, render_template, request, session, url_for
from pymongo import MongoClient, ReturnDocument
from pymongo.errors import PyMongoError, OperationFailure
from pymongo.server_api import ServerApi

from castcrew.layout import create_castcrew_insert_app, create_castcrew_update_app
from committee.layout import (
    create_committee_insert_app, create_committee_lookup_app, create_committee_update_app
)
from database import make_client, save_client, close_client
from members.callbacks import register_member_lookup_callbacks
from members.layout import members_lookup_layout
from people.callbacks import register_people_insert_callbacks, register_people_update_callbacks
from people.layout import people_insert_layout, people_update_layout
from productions.layout import (
    create_productions_lookup_app, create_festivals_insert_app,
    create_productions_insert_app, create_productions_update_app
)
from transactions.callbacks import register_transactions_insert_callbacks
from transactions.layout import transactions_insert_layout

APP_DIR = Path(__file__).resolve().parent
ENV_FILE = APP_DIR / ".env"

load_dotenv(dotenv_path=ENV_FILE, override=True)

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "")

dashboards = {}
for route in [
    'members/lookup',
    # 'productions/lookup', 'productions/insert', 'productions/update',
    # 'committee/lookup', 'committee/insert', 'committee/update',
    # 'castcrew/insert', 'castcrew/update',
    'people/insert', 'people/update',
    'transactions/insert',
]:
    dashboards[route] = Dash(
        __name__ + '_' + route.replace('/', '_'),
        server=app,
        url_base_pathname=f"/{route}/",
        suppress_callback_exceptions=True,
    )


@app.route("/set-debug-role", methods=["POST"])
def set_debug_role():
    if not app.debug:
        return "Not available", 404

    role = request.form.get("role", "Public")

    if role not in {"Public", "Committee", "Treasurer"}:
        role = "Awaiting Connection"

    session["debug_role"] = role

    return redirect(url_for("index"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")

    if not username or not password:
        username = os.getenv("USERNAME", "")
        password = os.getenv("PASSWORD", "")

    try:
        client = make_committee_client(username, password)
    except PyMongoError:
        return render_template(
            "login.html", error="Database connection unavailable."
        ), 503

    # Replace any previous login/session state.
    old_id = session.pop("db_session_id", None)
    if old_id:
        close_client(old_id)

    # Rotate the Flask session identifier to reduce session-fixation risk.
    session.clear()
    db_session_id = secrets.token_urlsafe(32)

    save_client(db_session_id, client)
    session["db_session_id"] = db_session_id

    db = client.myDatabase
    session["database"] = client.myDatabase
    user = db.users.find_one({'username': username})
    if user is None or user.get('role', 'Public') == 'Public':
        session["username"] = None
        session["role"] = "Public"

    elif user.get('role', 'Public') in {'Committee', 'Treasurer'}:
        session["username"] = username
        session["role"] = user['role']

    else:
        raise

    return redirect(url_for("index"))


@app.route("/public-login", methods=["POST"])
def public_login():
    username = os.getenv("USERNAME", "")
    password = os.getenv("PASSWORD", "")

    try:
        client = make_client(username, password)
    except PyMongoError:
        return redirect(
            url_for("index"), error="Database connection unavailable."
        ), 503

    # Replace any previous login/session state.
    old_id = session.pop("db_session_id", None)
    if old_id:
        close_client(old_id)

    # Rotate the Flask session identifier to reduce session-fixation risk.
    session.clear()
    db_session_id = secrets.token_urlsafe(32)

    save_client(db_session_id, client)
    session["role"] = "Public"
    session["db_session_id"] = db_session_id

    return redirect(url_for("index"))


@app.route("/debug-login", methods=["POST"])
def debug_login():
    username = os.getenv("USERNAME_ADMIN", "")
    password = os.getenv("PASSWORD_ADMIN", "")

    try:
        client = make_client(username, password)
    except PyMongoError:
        return redirect(
            url_for("index"), error="Database connection unavailable."
        ), 503

    # Replace any previous login/session state.
    old_id = session.pop("db_session_id", None)
    if old_id:
        close_client(old_id)

    # Rotate the Flask session identifier to reduce session-fixation risk.
    session.clear()
    db_session_id = secrets.token_urlsafe(32)

    save_client(db_session_id, client)
    session["debug_role"] = "Public"
    session["db_session_id"] = db_session_id

    return redirect(url_for("index"))


@app.route("/")
def index():
    if 'role' not in session.keys():
        session["role"] = "Awaiting Connection"
    if 'debug_role' not in session.keys():
        session["debug_role"] = "Awaiting Connection"

    role = session["debug_role"] if app.debug else session["role"]

    return render_template("index.html", role=role)


@app.route("/logout", methods=["POST"])
def logout():
    db_session_id = session.pop("db_session_id", None)

    if db_session_id:
        close_client(db_session_id)

    session.clear()
    return redirect(url_for("login"))


dashboards['members/lookup'].layout = members_lookup_layout
register_member_lookup_callbacks(dashboards['members/lookup'], app)
dashboards['people/insert'].layout = people_insert_layout
register_people_insert_callbacks(dashboards['people/insert'], app)
dashboards['people/update'].layout = people_update_layout
register_people_update_callbacks(dashboards['people/update'], app)
dashboards['transactions/insert'].layout = transactions_insert_layout
register_transactions_insert_callbacks(dashboards['transactions/insert'], app)
# members_lookup_app = create_members_lookup_app(app)
# productions_lookup_app = create_productions_lookup_app(app)
# festivals_insert_app = create_festivals_insert_app(app)
# productions_insert_app = create_productions_insert_app(app)
# productions_update_app = create_productions_update_app(app)
# committee_lookup_app = create_committee_lookup_app(app)
# committee_insert_app = create_committee_insert_app(app)
# committee_update_app = create_committee_update_app(app)
# people_insert_app = create_people_insert_app(app)
# people_update_app = create_people_update_app(app)
# castcrew_insert_app = create_castcrew_insert_app(app)
# castcrew_update_app = create_castcrew_update_app(app)
# transactions_insert_app = create_transactions_insert_app(app)

if __name__ == "__main__":
    # app.run(host="127.0.0.1", port=int(os.environ.get("PORT", "5000")), debug=False)
    app.run(debug=True)
