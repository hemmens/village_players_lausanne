import os
import secrets
from datetime import datetime, timedelta, timezone
from urllib.parse import quote

from flask import Flask, flash, redirect, render_template, request, session, url_for
from pymongo import MongoClient, ReturnDocument
from pymongo.errors import PyMongoError, OperationFailure
from pymongo.server_api import ServerApi

from committee.layout import (
    create_committee_insert_app, create_committee_lookup_app, create_committee_update_app
)
from members.layout import create_members_app

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", secrets.token_hex(32))

# MongoDB settings. Keep these on the server; never expose them to browser JS.
MONGODB_URI_TEMPLATE = os.environ.get(
    "MONGODB_URI_TEMPLATE",
    "mongodb+srv://{username}:{password}@vps-00.lk81a.mongodb.net/?retryWrites=true&w=majority&appName=VPS-00",
)
APP_DB_NAME = os.environ.get("APP_DB_NAME", "appdb")
LEASE_SECONDS = int(os.environ.get("PRIVILEGED_LEASE_SECONDS", "120"))


def utcnow():
    return datetime.now(timezone.utc)


def mongo_uri_for_credentials(username, password):
    # URI-encode credentials so special characters cannot break the URI.
    return MONGODB_URI_TEMPLATE.format(
        username=quote(username, safe=""),
        password=quote(password, safe=""),
    )


def authenticate(username, password):
    """Authenticate against MongoDB and return (role, client), or (None, None)."""
    if not username or not password:
        return None, None

    client = None
    try:
        uri = mongo_uri_for_credentials(username, password)
        client = MongoClient(uri, server_api=ServerApi('1')) #, serverSelectionTimeoutMS=5000)
        # Force authentication/connection now rather than relying on lazy connect.
        client.admin.command("ping")

        db = client[APP_DB_NAME]
        user = db.users.find_one({"username": username}, {"role": 1})

        # The MongoDB credentials are valid. Application role comes from users.role.
        role = (user or {}).get("role", "Member")
        if role not in {"Member", "Admin"}:
            role = "Member"
        return role, client
    except (PyMongoError, OperationFailure):
        if client:
            client.close()
        return None, None


def release_lease():
    token = session.get("lease_token")
    if token:
        # A separate application connection is used for the lease.
        client = MongoClient(os.environ["APP_MONGODB_URI"], serverSelectionTimeoutMS=5000)
        try:
            client[APP_DB_NAME].privileged_leases.delete_one(
                {"_id": "privileged", "token": token}
            )
        finally:
            client.close()
    session.pop("lease_token", None)


def acquire_lease(token, role):
    client = MongoClient(os.environ["APP_MONGODB_URI"], serverSelectionTimeoutMS=5000)
    try:
        db = client[APP_DB_NAME]
        now = utcnow()
        expires = now + timedelta(seconds=LEASE_SECONDS)

        # Atomic: succeeds only if no active privileged session exists.
        doc = db.privileged_leases.find_one_and_update(
            {
                "_id": "privileged",
                "$or": [
                    {"expires_at": {"$lte": now}},
                    {"token": token},
                ],
            },
            {
                "$set": {
                    "token": token,
                    "role": role,
                    "expires_at": expires,
                    "updated_at": now,
                }
            },
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )
        return bool(doc and doc.get("token") == token)
    finally:
        client.close()


def renew_lease():
    token = session.get("lease_token")
    if not token or session.get("role") not in {"Member", "Admin"}:
        return False

    client = MongoClient(os.environ["APP_MONGODB_URI"], serverSelectionTimeoutMS=5000)
    try:
        result = client[APP_DB_NAME].privileged_leases.update_one(
            {"_id": "privileged", "token": token},
            {
                "$set": {
                    "expires_at": utcnow() + timedelta(seconds=LEASE_SECONDS),
                    "updated_at": utcnow(),
                }
            },
        )
        return result.modified_count == 1 or result.matched_count == 1
    finally:
        client.close()


def current_role():
    if app.debug:
        return session.get("debug_role", "Public")

    role = session.get("role", "Public")
    if role in {"Committee", "Treasurer"}:
        if renew_lease():
            return role
        # Lease was lost/expired: safely fall back to Public.
        session["role"] = "Public"
        session.pop("lease_token", None)
    return "Public"


@app.before_request
def maintain_privileged_session():
    if request.endpoint not in {"login", "logout", "static"}:
        current_role()


@app.route("/", methods=["GET"])
def index():
    role = current_role()
    return render_template("index.html", role=role)


@app.route("/set-debug-role", methods=["POST"])
def set_debug_role():
    if not app.debug:
        return "Not available", 404

    role = request.form.get("role", "Public")

    if role not in {"Public", "Committee", "Treasurer"}:
        role = "Public"

    session["debug_role"] = role

    return redirect(url_for("index"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")

    # Existing privileged session is released before a new login attempt.
    release_lease()
    session.clear()

    role, client = authenticate(username, password)

    if role is None:
        # Per the requested behavior, missing/invalid credentials become Public.
        session["role"] = "Public"
        flash("Credentials were missing or invalid. You are using Public access.", "info")
        return redirect(url_for("index"))

    token = secrets.token_urlsafe(32)
    if not acquire_lease(token, role):
        # Valid credentials, but the single privileged slot is already occupied.
        if client:
            client.close()
        session["role"] = "Public"
        flash(
            "Your credentials are valid, but the privileged slot is currently in use. "
            "You are using Public access.",
            "info",
        )
        return redirect(url_for("index"))

    # Store no password in the Flask session.
    session["role"] = role
    session["username"] = username
    session["lease_token"] = token
    if client:
        client.close()

    flash(f"Signed in as {role}.", "success")
    return redirect(url_for("index"))


@app.route("/logout", methods=["POST"])
def logout():
    release_lease()
    session.clear()
    return redirect(url_for("index"))


@app.route("/api/data", methods=["GET"])
def read_data():
    role = current_role()

    client = MongoClient(os.environ["APP_MONGODB_URI"], serverSelectionTimeoutMS=5000)
    try:
        docs = list(
            client[APP_DB_NAME].items.find({}, {"_id": 0}).limit(100)
        )
        return {"role": role, "items": docs}
    finally:
        client.close()


@app.route("/api/data", methods=["POST"])
def write_data():
    role = current_role()
    if role not in {"Member", "Admin"}:
        return {"error": "Write access requires Member or Admin privileges."}, 403

    payload = request.get_json(silent=True) or {}
    value = str(payload.get("value", "")).strip()
    if not value:
        return {"error": "value is required."}, 400

    client = MongoClient(os.environ["APP_MONGODB_URI"], serverSelectionTimeoutMS=5000)
    try:
        client[APP_DB_NAME].items.insert_one(
            {
                "value": value,
                "created_by": session.get("username"),
                "created_at": utcnow(),
            }
        )
        return {"ok": True}
    finally:
        client.close()


@app.after_request
def no_store_for_auth_pages(response):
    if request.endpoint in {"login", "logout"}:
        response.headers["Cache-Control"] = "no-store"
    return response

members_app = create_members_app(app)
committee_lookup_app = create_committee_lookup_app(app)
committee_insert_app = create_committee_insert_app(app)
committee_update_app = create_committee_update_app(app)

if __name__ == "__main__":
    # app.run(host="127.0.0.1", port=int(os.environ.get("PORT", "5000")), debug=False)
    app.run(debug=True)
