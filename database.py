import os
import pandas as pd
# from urllib.parse import quote

from bson.decimal128 import Decimal128
from bson.objectid import ObjectId
from dotenv import load_dotenv
from flask import has_request_context
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

from variables import MEMBER_LIST_COLUMNS

load_dotenv()

# def create_user_client(username, password):
#     username = quote(username, safe="")
#     password = quote(password, safe="")

#     uri = os.environ.get("URI_TEMPLATE", "").format(
#         username=username,
#         password=password,
#     )

#     if not uri:
#         raise ValueError("Missing URI environment variable")

#     return MongoClient(
#         uri,
#         serverSelectionTimeoutMS=5000,
#     )

uri = os.getenv("URI_TEMPLATE", "")
uri = uri.replace("{{user}}", os.getenv("USERNAME_COMM", "")).replace("{{pw}}", os.getenv("PASSWORD_COMM", ""))

client = MongoClient(uri, server_api=ServerApi('1'), serverSelectionTimeoutMS=5000)
db = client.myDatabase

def get_names():
    if not has_request_context():
        return []

    return list(
        {
            'label': f"{x['surname']}, {x['first_name']}",
            'value': str(x['_id']) + '|' + x['first_name'] + ' ' + x['surname'],
        }
        for x in db.people.find({})
    )

def get_committee_positions():
    if not has_request_context():
        return []

    return list(
        {
            'label': f"{entry['season']} / {entry['position']}"
                f" / {db.people.find_one({'_id': entry['holder']})['surname']}",
            'value': str(entry['_id']),
        }
        for entry in db.committee.find({})
    )

def get_member_list(role, seasons, types, persons, columns):
    if not has_request_context() or role not in {"Committee", "Treasurer", "Public"}:
        return pd.DataFrame().to_dict('records')

    members = pd.DataFrame(
        db.members.find({
            'season': {'$in': seasons},
            'type': {'$in': types},
        })
    )
    if members.empty:
        return pd.DataFrame().to_dict('records')

    if persons:
        person_ids = [ObjectId(p.split('|')[0]) for p in persons]
        members = members[members['person'].isin(person_ids)]

    members.set_index('_id', inplace=True)
    people = pd.DataFrame(db.people.find()).set_index('_id')
    members = members.join(people, 'person')

    if role == "Public":
        members = members[['season', 'first_name', 'surname']]
    else:
        transactions = pd.DataFrame(
            db.transactions.find({'Type': 'Membership Subscription'})
        ).set_index('_id')[['Date', 'Amount']]

        try:
            members = members.join(transactions, 'transaction')
        except:
            pass

        mcols = [
            MEMBER_LIST_COLUMNS.get(col) for col in columns
            if MEMBER_LIST_COLUMNS.get(col) in members.columns
        ]
        for col in ['season', 'surname']:
            if col not in mcols:
                mcols.append(col)

        members = members[mcols]
        for col in ['gdpr', 'payment_amount', 'payment_date']:
            if col in members.columns:
                members[col] = members[col].astype(str)

    members.sort_values(['season', 'surname'], inplace=True)
    
    return members.to_dict('records')

def get_committee_list(role, seasons):
    if not has_request_context() or role not in {"Committee", "Treasurer", "Public"}:
        return pd.DataFrame().to_dict('records')

    committee = pd.DataFrame(db.committee.find({'season': {'$in': seasons}}))
    if committee.empty:
        return pd.DataFrame().to_dict('records')

    committee.set_index('_id', inplace=True)
    people = pd.DataFrame(db.people.find()).set_index('_id')
    committee = committee.join(people, 'holder')
    committee = committee[['season', 'position', 'first_name', 'surname', 'committee_email']]
    committee['committee_email'] = committee['committee_email'].fillna('')
    committee.position = committee.position.apply(lambda x: x.title())
    committee.sort_values('season', inplace=True)
    return committee.to_dict('records')

def insert_committee_member(person_id, season, position):
    # if not has_request_context():
    #     return {"error": "No request context."}, 400

    if not person_id or not season or not position:
        return "Person, season, and position are required." # {"error": "Person, season, and position are required."}, 400

    try:
        ObjectId(person_id)
    except Exception as e:
        return f"Invalid person ID: {e}" # {"error": f"Invalid person ID: {e}"}, 400

    committee_payload = {
        'holder': ObjectId(person_id),
        'season': season,
        'position': position
    }

    existing = db.committee.find_one(committee_payload)
    if existing:
        return {"error": "Committee member already exists"}, 400

    new_committee_member = db.committee.insert_one(committee_payload)

    return f"New committee member: {str(new_committee_member.inserted_id)}" # {"ok": True}, 201

def delete_committee_member(committee_id):
    # if not has_request_context():
    #     return {"error": "No request context."}, 400

    if not committee_id:
        return "Committee member ID is required." # {"error": "Committee member ID is required."}, 400

    try:
        ObjectId(committee_id)
    except Exception as e:
        return f"Invalid committee member ID: {e}" # {"error": f"Invalid committee member ID: {e}"}, 400

    result = db.committee.delete_one({'_id': ObjectId(committee_id)})
    if result.deleted_count == 0:
        return "Committee member not found" # {"error": "Committee member not found"}, 404

    return "Committee member deleted successfully" # {"ok": True}, 200
