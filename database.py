import os
import pandas as pd
from datetime import datetime
from urllib.parse import quote

from bson.decimal128 import Decimal128
from bson.objectid import ObjectId
from dotenv import load_dotenv
from flask import has_request_context, session
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pymongo.errors import PyMongoError

from update_mapping import update_mapping
from variables import MEMBER_LIST_COLUMNS

load_dotenv()

_clients = {}


def make_client(username, password):
    username = quote(username, safe="")
    password = quote(password, safe="")

    uri = os.getenv("URI_TEMPLATE", "")
    uri_pw = uri.replace("{{user}}", username).replace("{{pw}}", password)

    client = MongoClient(uri_pw, server_api=ServerApi('1'), serverSelectionTimeoutMS=5000)

    try:
        client.admin.command("ping")
        return client
    except PyMongoError:
        client.close()

    uri_pub = uri.replace("{{user}}", os.getenv("USERNAME", "")).replace("{{pw}}", os.getenv("PASSWORD", ""))
    client = MongoClient(uri_pub, server_api=ServerApi('1'), serverSelectionTimeoutMS=5000)

    try:
        client.admin.command("ping")
        return client
    except:
        client.close()
        raise


def save_client(session_id, client):
    close_client(session_id)
    _clients[session_id] = client


def get_database(session_id):
    client = _clients.get(session_id)
    return client.myDatabase


def close_client(session_id):
    client = _clients.pop(session_id, None)
    if client is not None:
        client.close()


def convert_date(date_str):
    date = date_str.split('T')[0].split('-')
    return datetime(
        int(date[0]), int(date[1]), int(date[2])
    )


def handle_decimal(amount: float) -> str:
    if (100 * amount) % 100 == 0:
        return Decimal128('%i' % amount)
    else:
        return Decimal128('%.2f' % amount)


def get_new_ref(date):
    db = get_database(session["db_session_id"])
    season = date.year % 100 + int(date.month >= 6)
    latest_refs = [
        x['Reference'] for x in db.transactions.find(
            {'Reference': {'$gt': season*1000, '$lt': (season + 1)*1000}}
        )
    ]

    if len(latest_refs):
        return max(latest_refs) + 1
    else:
        return season*1000 + 1


def extract_name(name):
    if name is None:
        return None

    name_split = name.split(',')
    first_name = name_split[1].strip()
    surname = name_split[0].strip()
    full_name = first_name + ' ' + surname
    return {
        'first_name': first_name,
        'surname': surname,
        'full_name': full_name,
    }


def find_collection_link(document_id, collection, field):
    return collection.find_one({field: document_id})


def get_names(add_empty=False):
    if not has_request_context():
        return []

    db = get_database(session["db_session_id"])
    names = list(
        {
            'label': f"{x['surname']}, {x['first_name']}",
            'value': str(x['_id']) + '|' + x['first_name'] + ' ' + x['surname'],
        }
        for x in db.people.find({})
    )
    if add_empty:
        names = [''] + names
    return names


def get_festivals(add_empty=False):
    if not has_request_context():
        return []

    db = get_database(session["db_session_id"])

    festivals = list(
        {
            'label': f"{f['title']} ({f['open_date'].year})",
            'value': str(f['_id'])
        }
        for f in db.festivals.find({})
    )
    if add_empty:
        festivals = [''] + festivals
    return festivals


def get_productions(add_empty=False):
    if not has_request_context():
        return []

    db = get_database(session["db_session_id"])

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

    shows = shows['label'].to_list()
    if add_empty:
        shows = [''] + shows
    return shows


def get_names_for_person_update():
    if not has_request_context():
        return []

    db = get_database(session["db_session_id"])

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

    db = get_database(session["db_session_id"])

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

    db = get_database(session["db_session_id"])

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
    db = get_database(session["db_session_id"])
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

    db_field = update_mapping[collection]['value'].get(field, '')
    if not db_field:
        db_field = update_mapping[collection]['date'].get(field, '')
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

# ---- MEMBERS ----



# ---- PRODUCTIONS ----

def get_production_details(production_id):
    db = session["database"]
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
                {'detail': 'Venue', 'info': festival.get('venue', '')}
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
        {'detail': 'Author', 'info': production.get('author', '')},
    ]

    festival_name = None
    if production.get('festival'):
        production = db.festivals.find_one({'_id': production['festival']})
        festival_name = production['title']

    row_data += [
        {'detail': 'Opening Date', 'info': production['open_date'].date().strftime('%d %B %Y')},
        {'detail': 'Closing Date', 'info': production['close_date'].date().strftime('%d %B %Y')},
        {'detail': 'Venue', 'info': production.get('venue', '')}
    ]
    if festival_name is not None:
        row_data.append({'detail': 'Festival', 'info': festival_name})

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


def insert_festival(name, venue, open, close):
    db = session["database"]
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


def insert_production(name, venue, author, open, close, festival_id):
    db = session["database"]
    # if not has_request_context():
    #     return {"error": "No request context."}, 400

    if not name or not (festival_id or (open and close)):
        return "Name and either performance dates or festival are required." # {"error": "Person, season, and position are required."}, 400

    production_payload = {'title': name}
    if festival_id:
        try:
            festival_id = ObjectId(festival_id)
        except Exception as e:
            return f"Invalid festival ID: {e}" # {"error": f"Invalid person ID: {e}"}, 400

        production_payload['festival'] = festival_id
        production_filter = production_payload.copy()
    else:
        production_payload['open_date'] = convert_date(open)
        production_payload['close_date'] = convert_date(close)
        production_filter = {
            'title': production_payload['title'],
            'open_date': {'$lte': production_payload['close_date']},
            'close_date': {'$gte': production_payload['open_date']},
        }

    if db.productions.find_one(production_filter):
        return "Production already exists" # {"error": "Committee member already exists"}, 400

    if venue:
        production_payload['venue'] = venue
    if author:
        production_payload['author'] = author

    new_production = db.productions.insert_one(production_payload)

    return f"New production: {str(new_production.inserted_id)}" # {"ok": True}, 201


def update_production(production_id, venue, author, open_date, close_date, festival_id):
    db = session["database"]
    if not has_request_context():
        return "" # {"error": "No request context."}, 400

    if not production_id:
        return "Person ID is required." # {"error": "Committee member ID is required."}, 400

    try:
        production_id = ObjectId(production_id)
    except Exception as e:
        return f"Invalid production ID: {e}" # {"error": f"Invalid committee member ID: {e}"}, 400

    if festival_id:
        try:
            festival_id = ObjectId(festival_id)
        except Exception as e:
            return f"Invalid festival ID: {e}" # {"error": f"Invalid committee member ID: {e}"}, 400

    update_payload = {
        '$set': {},
        '$unset': {}
    }

    if venue:
        update_payload['$set']['venue'] = venue
    else:
        update_payload['$unset']['venue'] = ""

    if author:
        update_payload['$set']['author'] = author
    else:
        update_payload['$unset']['author'] = ""

    if open_date:
        update_payload['$set']['open_date'] = convert_date(open_date)
    else:
        update_payload['$unset']['open_date'] = ""

    if close_date:
        update_payload['$set']['close_date'] = convert_date(close_date)
    else:
        update_payload['$unset']['close_date'] = ""

    if festival_id:
        update_payload['$set']['festival'] = festival_id
    else:
        update_payload['$unset']['festival'] = ""

    result = db.productions.update_one({'_id': production_id}, update_payload)
    if result.modified_count == 0:
        return "Production not found or no data changes" # {"error": "Committee member not found"}, 404

    return "Production updated successfully" # {"ok": True}, 200


def delete_production(production_id):
    db = session["database"]
    # if not has_request_context():
    #     return {"error": "No request context."}, 400

    if not production_id:
        return "Production ID is required." # {"error": "Committee member ID is required."}, 400

    try:
        production_id = ObjectId(production_id)
    except Exception as e:
        return f"Invalid person ID: {e}" # {"error": f"Invalid committee member ID: {e}"}, 400

    if find_collection_link(production_id, db.transactions, 'Production'):
        return "Production cannot be deleted - link to Transactions"
    if find_collection_link(production_id, db.castcrew, 'production'):
        return "Production cannot be deleted - link to Cast & Crew"

    result = db.productions.delete_one({'_id': production_id})
    if result.deleted_count == 0:
        return "Production not found" # {"error": "Committee member not found"}, 404

    return "Production deleted successfully" # {"ok": True}, 200

# ---- COMMITTEE ----

def get_committee_list(role, seasons):
    db = session["database"]
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
    db = session["database"]
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
    db = session["database"]
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

# ---- PEOPLE ----



# ---- CAST & CREW ----

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


def update_castcrew(castcrew_id, name):
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

    if name:
        update_payload['$set']['role_name'] = name
    else:
        update_payload['$unset']['role_name'] = ""

    result = db.castcrew.update_one({'_id': castcrew_id}, update_payload)
    if result.modified_count == 0:
        return "Role not found or no data changes" # {"error": "Committee member not found"}, 404

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

# ---- TRANSACTIONS ----


