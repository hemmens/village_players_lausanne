# village_players

# MongoDB Role App

A small Flask/PyMongo web application implementing:

- Public / Member / Admin roles.
- Missing or invalid credentials => Public.
- Valid credentials are authenticated by MongoDB.
- Application role is read from `appdb.users.role`.
- Public sessions can coexist.
- At most one Member/Admin session holds the privileged lease.
- Member/Admin can write; Public cannot.
- Privileged access uses a MongoDB-backed lease so multiple web workers share the same lock.
- Passwords are never stored in the Flask session.

## Important security design

The browser must never construct or receive the MongoDB URI. The username/password from the login form are sent to Flask over HTTPS; Flask URL-encodes them and constructs the URI server-side.

The `APP_MONGODB_URI` account should be a separate least-privilege application account. It is used for the lease and application data operations.

## User collection

Create users such as:

```javascript
db.users.insertMany([
  { username: "member1", role: "Member" },
  { username: "admin1", role: "Admin" }
])
```

The actual password is the MongoDB password for that username, not a field stored in `users`.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Set the variables in .env, then export them or use your deployment's secret manager.
python app.py
```

Database client sessions expire after `DB_SESSION_TTL_SECONDS` seconds. The
default is 60 seconds for testing; set it to `43200` for a 12-hour lifetime.
Expired clients are closed on the next request, and the user must log in again.
Client sessions are held in process memory, so restarting or redeploying the app
also clears them; a browser with a stale session will be sent to the login page.
Each worker has its own in-memory sessions, so multi-worker deployments require
a shared session/client design to avoid requests landing on a different worker.

For production, run behind HTTPS with a WSGI server such as Gunicorn:

```bash
gunicorn -w 2 -b 127.0.0.1:8000 app:app
```

Use a reverse proxy (for example nginx) for TLS and set secure cookie settings appropriate to your deployment.

## Production hardening to add

- HTTPS only.
- CSRF protection for POST requests.
- Rate limiting / account lockout for repeated login attempts.
- Strong Flask secret key stored in a secret manager.
- `SESSION_COOKIE_SECURE=True`, `SESSION_COOKIE_HTTPONLY=True`, and an appropriate `SESSION_COOKIE_SAMESITE`.
- Audit logging for privileged operations.
- Least-privilege MongoDB roles.
- Input validation and authorization on every write/admin endpoint.
- Do not expose MongoDB directly to the public Internet.
