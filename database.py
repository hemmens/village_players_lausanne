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
    names = pd.DataFrame(names).sort_values('label')
    names = names.to_dict('records')
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


def get_members(add_empty=False):
    if not has_request_context():
        return []

    db = get_database(session["db_session_id"])

    members = pd.DataFrame(db.members.find({}))
    people = pd.DataFrame(db.people.find({})).set_index('_id')
    members = members.join(people, 'person')
    members.sort_values(
        ['season', 'surname', 'first_name'], ascending=[False, True, True], inplace=True
    )
    members['member_label'] = members.apply(
        lambda row:{
            'label': f"{row['first_name']} {row['surname']} / {row['season']} / {row['type']}",
            'value': str(row['_id'])
        }, axis=1
    )

    member_list = members.member_label.to_list()
    if add_empty:
        member_list = [''] + member_list
    return member_list


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
