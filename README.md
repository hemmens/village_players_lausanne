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
