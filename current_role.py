from flask import has_request_context, session

# from app import renew_lease

def current_role(server):
    """
    Returns the current role from the session.
    """
    if not has_request_context():
        return "Public"

    if server.debug:
        return session.get("debug_role", "Public")

    role = session.get("role", "Public")
    # if role in {"Committee", "Treasurer"}:
    #     if renew_lease():
    #         return role

    #     session["role"] = "Public"
    #     session.pop("lease_token", None)

    return role
