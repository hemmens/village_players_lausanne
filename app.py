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

from castcrew.callbacks import (
    register_castcrew_insert_callbacks, register_castcrew_update_callbacks
)
from castcrew.layout import castcrew_insert_layout, castcrew_update_layout
from committee.callbacks import (
    register_committee_insert_callbacks, register_committee_lookup_callbacks,
    register_committee_update_callbacks
)
from committee.layout import (
    committee_insert_layout, committee_lookup_layout, committee_update_layout
)
from database import make_client, save_client, close_client
from members.callbacks import register_member_lookup_callbacks, register_member_search_callbacks
from members.layout import members_lookup_layout, members_search_layout
from people.callbacks import register_people_insert_callbacks, register_people_update_callbacks
from people.layout import people_insert_layout, people_update_layout
from productions.callbacks import (
    register_productions_insert_callbacks, register_productions_lookup_callbacks,
    register_productions_update_callbacks
)
from productions.layout import (
    productions_insert_layout, productions_lookup_layout, productions_update_layout
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
    'members/lookup', 'members/search',
    'productions/lookup', 'productions/insert', 'productions/update',
    'committee/lookup', 'committee/insert', 'committee/update',
    'castcrew/insert', 'castcrew/update',
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
        client = make_client(username, password)
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

    users = client.myDatabase.dbusers
    user = users.find_one({'username': username})
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
        print("Error: Database connection unavailable.")
        return redirect(url_for("index"))

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
    else:
        session["debug_role"] = session["role"]

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
    return redirect(url_for("index"))


dashboards['members/lookup'].layout = members_lookup_layout
register_member_lookup_callbacks(dashboards['members/lookup'], app)
dashboards['members/search'].layout = members_search_layout
register_member_search_callbacks(dashboards['members/search'])
dashboards['productions/lookup'].layout = productions_lookup_layout
register_productions_lookup_callbacks(dashboards['productions/lookup'], app)
dashboards['productions/insert'].layout = productions_insert_layout
register_productions_insert_callbacks(dashboards['productions/insert'], app)
dashboards['productions/update'].layout = productions_update_layout
register_productions_update_callbacks(dashboards['productions/update'], app)
dashboards['committee/lookup'].layout = committee_lookup_layout
register_committee_lookup_callbacks(dashboards['committee/lookup'], app)
dashboards['committee/insert'].layout = committee_insert_layout
register_committee_insert_callbacks(dashboards['committee/insert'], app)
dashboards['committee/update'].layout = committee_update_layout
register_committee_update_callbacks(dashboards['committee/update'], app)
dashboards['castcrew/insert'].layout = castcrew_insert_layout
register_castcrew_insert_callbacks(dashboards['castcrew/insert'], app)
dashboards['castcrew/update'].layout = castcrew_update_layout
register_castcrew_update_callbacks(dashboards['castcrew/update'], app)
dashboards['people/insert'].layout = people_insert_layout
register_people_insert_callbacks(dashboards['people/insert'], app)
dashboards['people/update'].layout = people_update_layout
register_people_update_callbacks(dashboards['people/update'], app)
dashboards['transactions/insert'].layout = transactions_insert_layout
register_transactions_insert_callbacks(dashboards['transactions/insert'], app)

if __name__ == "__main__":
    # app.run(host="127.0.0.1", port=int(os.environ.get("PORT", "5000")), debug=False)
    app.run(debug=True)
