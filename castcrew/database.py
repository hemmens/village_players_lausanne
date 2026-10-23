from bson.objectid import ObjectId
from flask import has_request_context, session

from database import get_database

def insert_castcrew(person_id, production_id, role, name):
    if not has_request_context():
        return ""

    if not person_id or not production_id or not role:
        return "Person, Production, and Role are required"
    
    db = get_database(session["db_session_id"])

    cast_crew_payload = {
        'person': ObjectId(person_id.split('|')[0]),
        'production': ObjectId(production_id),
        'role': role
    }

    if db.castcrew.find_one(cast_crew_payload):
        return "Cast or Crew Member already exists"

    if name:
        cast_crew_payload['role_name'] = name

    new_castcrew = db.castcrew.insert_one(cast_crew_payload)

    return f"New Cast or Crew Member: {str(new_castcrew.inserted_id)}"


def update_castcrew(castcrew_id, name):
    if not has_request_context():
        return ""

    if not castcrew_id:
        return "Role ID is required"

    try:
        castcrew_id = ObjectId(castcrew_id)
    except Exception as e:
        return f"Invalid role ID: {e}"
    
    db = get_database(session["db_session_id"])

    update_payload = {
        '$set': {},
        '$unset': {}
    }

    if name:
        update_payload['$set']['role_name'] = name
    else:
        update_payload['$unset']['role_name'] = ""

    result = db.castcrew.update_one({'_id': castcrew_id}, update_payload)
    if result.modified_count == 0:
        return "Role not found or no data changes"

    return "Role updated successfully"


def delete_castcrew(castcrew_id):
    if not has_request_context():
        return ""

    if not castcrew_id:
        return "Role ID is required"

    try:
        castcrew_id = ObjectId(castcrew_id)
    except Exception as e:
        return f"Invalid role ID: {e}"
    
    db = get_database(session["db_session_id"])

    result = db.castcrew.delete_one({'_id': castcrew_id})
    if result.deleted_count == 0:
        return "Role not found"

    return "Role deleted successfully"
