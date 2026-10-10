import os
import pandas as pd
from datetime import datetime
# from urllib.parse import quote

from bson.decimal128 import Decimal128
from bson.objectid import ObjectId
from dotenv import load_dotenv
from flask import has_request_context
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

from update_mapping import update_mapping
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

def convert_date(date_str):
    date = date_str.split('T')[0].split('-')
    return datetime(
        int(date[0]), int(date[1]), int(date[2])
    )

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

def get_festivals():
    if not has_request_context():
        return []

    return list(
        {
            'label': f"{f['title']} ({f['open_date'].year})",
            'value': str(f['_id'])
        }
        for f in db.festivals.find({})
    )

def get_productions():
    if not has_request_context():
        return []

    festivals = {
        str(f['_id']): {
            'title': f['title'],
            'date': f['open_date'],
        }
        for f in db.festivals.find({})
    }
    productions = {
        str(p['_id']): {
            'title': p['title'],
            'date': p['open_date']
                if p.get('open_date') else
                festivals[str(p['festival'])]['date'],
        }
        for p in db.productions.find({})
    }

    shows = pd.concat([
        pd.DataFrame.from_dict(festivals, orient='index'),
        pd.DataFrame.from_dict(productions, orient='index'),
    ])
    shows.sort_values('date', ascending=False, inplace=True)
    shows.reset_index(inplace=True, names='db_id')
    shows['label'] = shows.apply(
        lambda row: {'label': f"{row.title} ({row.date.year})", 'value': row.db_id}, axis=1
    )

    return shows['label'].to_list()

def get_names_for_person_update():
    if not has_request_context():
        return []

    return list(
        {
            'label': f"{x['first_name']} {x['surname']}",
            'value': str(x['_id']),
        }
        for x in db.people.find({})
    )

def get_committee_positions():
    if not has_request_context():
        return []

    positions = list(
        {
            'label': f"{entry['season']} / {entry['position']}"
                f" / {db.people.find_one({'_id': entry['holder']})['surname']}",
            'value': str(entry['_id']),
        }
        for entry in db.committee.find({})
    )
    positions.reverse()
    return positions

def get_castcrew():
    if not has_request_context():
        return []

    return list(
        {
            'label': f"{db.productions.find_one({'_id': x['production']})['title']}"
                    f" / {db.people.find_one({'_id': x['person']})['surname']}"
                    f" / {x['role']}",
            'value': str(x['_id']),
        }
        for x in db.castcrew.find({})
    )

def update_form_fill_in_value(collection, field, document_id):
    if not has_request_context():
        return ""

    if not collection or not field or not document_id:
        return ""

    try:
        document_id = ObjectId(document_id)
    except Exception as e:
        return ""

    document = db[collection].find_one({"_id": document_id})
    if not document:
        return ""

    db_field = update_mapping[collection]['value'].get(field, field)
    if db_field not in document:
        return ""

    value = document[db_field]
    if isinstance(value, Decimal128):
        value = float(value.to_decimal())
    if isinstance(value, ObjectId):
        value = str(value)
    if isinstance(value, bool):
        value = ["private"] if value else []

    return value

def find_collection_link(document_id, collection, field):
    return collection.find_one({field: document_id})

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

def get_production_details(production_id):
    if not production_id:
        return pd.DataFrame().to_dict('records')

    festival = db.festivals.find_one({'_id': ObjectId(production_id)})
    if festival:
        productions = db.productions.find({'festival': ObjectId(production_id)})
        return pd.DataFrame(
            [
                {'detail': 'Title', 'info': festival['title']},
                {'detail': 'Opening Date', 'info': festival['open_date'].date().strftime('%d %B %Y')},
                {'detail': 'Closing Date', 'info': festival['close_date'].date().strftime('%d %B %Y')},
                {'detail': 'Venue', 'info': festival['venue']}
            ] + [
                {'detail': 'Play', 'info': f"{production['title']} by {production['author']}"}
                for production in productions
            ]
        ).to_dict('records')

    production = db.productions.find_one({'_id': ObjectId(production_id)})
    if not production:
        return pd.DataFrame().to_dict('records')

    row_data = [
        {'detail': 'Title', 'info': production['title']},
        {'detail': 'Author', 'info': production['author']},
    ]

    if production.get('festival'):
        production = db.festivals.find_one({'_id': production['festival']})

    row_data += [
        {'detail': 'Opening Date', 'info': production['open_date'].date().strftime('%d %B %Y')},
        {'detail': 'Closing Date', 'info': production['close_date'].date().strftime('%d %B %Y')},
        {'detail': 'Venue', 'info': production['venue']}
    ]

    castcrew = db.castcrew.find({'production': ObjectId(production_id)})
    for participant in castcrew:
        character = participant.get('role_name')
        person = db.people.find_one({'_id': participant['person']})
        row_data.append(
            {
                'detail': participant['role'] if not character else character,
                'info': f"{person['first_name']} {person['surname']}",
            }
        )

    return pd.DataFrame(row_data).to_dict('records')

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
        'position': position.lower(),
    }

    if db.committee.find_one(committee_payload):
        return "Committee member already exists" # {"error": "Committee member already exists"}, 400

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

def insert_person(first_name, surname, address, postcode, address_private, home_phone,
        home_phone_private, mobile, mobile_private, email, email_private, gender,
        gdpr, committee_email):
    # if not has_request_context():
    #     return {"error": "No request context."}, 400

    if not first_name or not surname:
        return "First name and surname are required." # {"error": "Person, season, and position are required."}, 400

    person_payload = {
        'first_name': first_name,
        'surname': surname
    }

    if db.people.find_one(person_payload):
        return "Person already exists" # {"error": "Committee member already exists"}, 400

    if address:
        person_payload['address'] = address
    if postcode:
        person_payload['postcode'] = postcode
    if address_private:
        person_payload['address_private'] = (address_private == ['private'])
    if home_phone:
        person_payload['home_phone'] = home_phone
    if home_phone_private:
        person_payload['home_phone_private'] = (home_phone_private == ['private'])
    if mobile:
        person_payload['mobile'] = mobile
    if mobile_private:
        person_payload['mobile_private'] = (mobile_private == ['private'])
    if email:
        person_payload['email'] = email
    if email_private:
        person_payload['email_private'] = (email_private == ['private'])
    if gender:
        person_payload['gender'] = gender
    if gdpr:
        person_payload['gdpr'] = convert_date(gdpr)
    if committee_email:
        person_payload['committee_email'] = (
            committee_email if '@' in committee_email else f'{committee_email}@villageplayers.ch'
        )

    new_person = db.people.insert_one(person_payload)

    return f"New person: {str(new_person.inserted_id)}" # {"ok": True}, 201

def update_person(person_id, address, postcode, address_private, home_phone,
        home_phone_private, mobile, mobile_private, email, email_private, gender,
        gdpr, committee_email):
    if not has_request_context():
        return "" # {"error": "No request context."}, 400

    if not person_id:
        return "Person ID is required." # {"error": "Committee member ID is required."}, 400

    try:
        person_id = ObjectId(person_id)
    except Exception as e:
        return f"Invalid person ID: {e}" # {"error": f"Invalid committee member ID: {e}"}, 400

    update_payload = {
        '$set': {},
        '$unset': {}
    }

    if address:
        update_payload['$set']['address'] = address
    else:
        update_payload['$unset']['address'] = ""

    if postcode:
        update_payload['$set']['postcode'] = postcode
    else:
        update_payload['$unset']['postcode'] = ""

    if address_private:
        update_payload['$set']['address_private'] = (address_private == ['private'])
    else:
        update_payload['$unset']['address_private'] = ""

    if home_phone:
        update_payload['$set']['home_phone'] = home_phone
    else:
        update_payload['$unset']['home_phone'] = ""

    if home_phone_private:
        update_payload['$set']['home_phone_private'] = (home_phone_private == ['private'])
    else:
        update_payload['$unset']['home_phone_private'] = ""

    if mobile:
        update_payload['$set']['mobile'] = mobile
    else:
        update_payload['$unset']['mobile'] = ""

    if mobile_private:
        update_payload['$set']['mobile_private'] = (mobile_private == ['private'])
    else:
        update_payload['$unset']['mobile_private'] = ""

    if email:
        update_payload['$set']['email'] = email
    else:
        update_payload['$unset']['email'] = ""

    if email_private:
        update_payload['$set']['email_private'] = (email_private == ['private'])
    else:
        update_payload['$unset']['email_private'] = ""

    if gender:
        update_payload['$set']['gender'] = gender
    else:
        update_payload['$unset']['gender'] = ""

    if gdpr:
        update_payload['$set']['gdpr'] = convert_date(gdpr)
    else:
        update_payload['$unset']['gdpr'] = ""

    if committee_email:
        update_payload['$set']['committee_email'] = (
            committee_email if '@' in committee_email else f'{committee_email}@villageplayers.ch'
        )
    else:
        update_payload['$unset']['committee_email'] = ""

    result = db.people.update_one({'_id': person_id}, update_payload)
    if result.modified_count == 0:
        return "Person not found" # {"error": "Committee member not found"}, 404

    return "Person updated successfully" # {"ok": True}, 200

def delete_person(person_id):
    # if not has_request_context():
    #     return {"error": "No request context."}, 400

    if not person_id:
        return "Person ID is required." # {"error": "Committee member ID is required."}, 400

    try:
        person_id = ObjectId(person_id)
    except Exception as e:
        return f"Invalid person ID: {e}" # {"error": f"Invalid committee member ID: {e}"}, 400

    if find_collection_link(person_id, db.members, 'person'):
        return "Person cannot be deleted - link to Members"
    if find_collection_link(person_id, db.transactions, 'Recipient'):
        return "Person cannot be deleted - link to Transactions"
    if find_collection_link(person_id, db.castcrew, 'person'):
        return "Person cannot be deleted - link to Cast & Crew"
    if find_collection_link(person_id, db.committee, 'holder'):
        return "Person cannot be deleted - link to Committee"

    result = db.people.delete_one({'_id': person_id})
    if result.deleted_count == 0:
        return "Person not found" # {"error": "Committee member not found"}, 404

    return "Person deleted successfully" # {"ok": True}, 200

def insert_castcrew(person_id, production_id, role, name):
    # if not has_request_context():
    #     return {"error": "No request context."}, 400

    if not person_id or not production_id or not role:
        return "Person, Production, and Role are required." # {"error": "Person, season, and position are required."}, 400

    cast_crew_payload = {
        'person': ObjectId(person_id.split('|')[0]),
        'production': ObjectId(production_id),
        'role': role
    }

    if db.castcrew.find_one(cast_crew_payload):
        return "Cast or Crew Member already exists" # {"error": "Committee member already exists"}, 400

    if name:
        cast_crew_payload['role_name'] = name

    new_castcrew = db.castcrew.insert_one(cast_crew_payload)

    return f"New Cast or Crew Member: {str(new_castcrew.inserted_id)}" # {"ok": True}, 201

def update_castcrew(castcrew_id, role_name):
    if not has_request_context():
        return "" # {"error": "No request context."}, 400

    if not castcrew_id:
        return "Role ID is required." # {"error": "Committee member ID is required."}, 400

    try:
        castcrew_id = ObjectId(castcrew_id)
    except Exception as e:
        return f"Invalid role ID: {e}" # {"error": f"Invalid committee member ID: {e}"}, 400

    update_payload = {
        '$set': {},
        '$unset': {}
    }

    if role_name:
        update_payload['$set']['role_name'] = role_name
    else:
        update_payload['$unset']['role_name'] = ""

    result = db.castcrew.update_one({'_id': castcrew_id}, update_payload)
    if result.modified_count == 0:
        return "Role not found" # {"error": "Committee member not found"}, 404

    return "Role updated successfully" # {"ok": True}, 200

def delete_castcrew(castcrew_id):
    # if not has_request_context():
    #     return {"error": "No request context."}, 400

    if not castcrew_id:
        return "Role ID is required." # {"error": "Committee member ID is required."}, 400

    try:
        castcrew_id = ObjectId(castcrew_id)
    except Exception as e:
        return f"Invalid role ID: {e}" # {"error": f"Invalid committee member ID: {e}"}, 400

    result = db.castcrew.delete_one({'_id': castcrew_id})
    if result.deleted_count == 0:
        return "Role not found" # {"error": "Committee member not found"}, 404

    return "Role deleted successfully" # {"ok": True}, 200

def insert_festival(name, venue, open, close):
    # if not has_request_context():
    #     return {"error": "No request context."}, 400

    if not name or not open or not close:
        return "Name and performance dates are required." # {"error": "Person, season, and position are required."}, 400

    festival_payload = {'title': name}

    if db.festivals.find_one(festival_payload):
        return "Festival name already exists" # {"error": "Committee member already exists"}, 400

    festival_payload['open_date'] = convert_date(open)
    festival_payload['close_date'] = convert_date(close)
    if venue:
        festival_payload['venue'] = venue

    new_festival = db.festivals.insert_one(festival_payload)

    return f"New festival: {str(new_festival.inserted_id)}" # {"ok": True}, 201

def insert_production(name, venue, open, close):
    # if not has_request_context():
    #     return {"error": "No request context."}, 400

    if not name or not open or not close:
        return "Name and performance dates are required." # {"error": "Person, season, and position are required."}, 400

    festival_payload = {'title': name}

    if db.festivals.find_one(festival_payload):
        return "Festival name already exists" # {"error": "Committee member already exists"}, 400

    festival_payload['open_date'] = convert_date(open)
    festival_payload['close_date'] = convert_date(close)
    if venue:
        festival_payload['venue'] = venue

    new_festival = db.festivals.insert_one(festival_payload)

    return f"New festival: {str(new_festival.inserted_id)}" # {"ok": True}, 201
