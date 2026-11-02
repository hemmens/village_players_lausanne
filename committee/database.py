import pandas as pd

from bson.objectid import ObjectId
from flask import has_request_context, session

from database import get_database

def get_committee_list(role, seasons):
    if not has_request_context() or role not in {"Committee", "Treasurer", "Public"}:
        return pd.DataFrame().to_dict('records')

    if "db_session_id" not in session.keys():
        return pd.DataFrame().to_dict('records')
    
    db = get_database(session["db_session_id"])

    committee = pd.DataFrame(db.committee.find({'season': {'$in': seasons}}))
    if committee.empty:
        return pd.DataFrame().to_dict('records')

    committee.set_index('_id', inplace=True)
    people = pd.DataFrame(db.people.find()).set_index('_id')
    committee = committee.join(people, 'holder')
    committee['full_name'] = committee.apply(lambda row: f"{row.first_name} {row.surname}", axis=1)
    committee = committee[['season', 'position', 'full_name', 'committee_email', 'list_rank']]
    committee['committee_email'] = committee['committee_email'].fillna('')
    committee.position = committee.position.apply(lambda x: x.title())
    if 'list_rank' not in committee.columns:
        committee['list_rank'] = 0
    committee.sort_values(['season', 'list_rank'], inplace=True)
    return committee.to_dict('records')


def insert_committee_member(person_id, season, position, list_rank):
    if not has_request_context():
        return ""

    if not person_id or not season or not position:
        return "Person, season, and position are required"

    try:
        ObjectId(person_id)
    except Exception as e:
        return f"Invalid person ID: {e}"
    
    db = get_database(session["db_session_id"])

    committee_payload = {
        'holder': ObjectId(person_id),
        'season': season,
        'position': position.lower(),
    }

    if list_rank:
        committee_payload['list_rank'] = int(list_rank)

    if db.committee.find_one(committee_payload):
        return "Committee member already exists"

    new_committee_member = db.committee.insert_one(committee_payload)

    return f"New committee member: {str(new_committee_member.inserted_id)}"


def update_committee_member(committee_id, list_rank):
    if not has_request_context():
        return ""

    if not committee_id:
        return "Committee member ID is required"

    try:
        ObjectId(committee_id)
    except Exception as e:
        return f"Invalid committee member ID: {e}"

    update_payload = {
        '$set': {},
        '$unset': {}
    }

    if list_rank:
        update_payload['$set']['list_rank'] = int(list_rank)
    else:
        update_payload['$unset']['list_rank'] = ""

    db = get_database(session["db_session_id"])

    result = db.committee.update_one({'_id': ObjectId(committee_id)}, update_payload)
    if result.modified_count == 0:
        return "Committee member not found"

    return "Committee member updated successfully"


def delete_committee_member(committee_id):
    if not has_request_context():
        return ""

    if not committee_id:
        return "Committee member ID is required"

    try:
        ObjectId(committee_id)
    except Exception as e:
        return f"Invalid committee member ID: {e}"

    db = get_database(session["db_session_id"])

    result = db.committee.delete_one({'_id': ObjectId(committee_id)})
    if result.deleted_count == 0:
        return "Committee member not found"

    return "Committee member deleted successfully"
