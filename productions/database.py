import pandas as pd

from bson.objectid import ObjectId
from flask import has_request_context, session

from database import convert_date, find_collection_link, get_database

def get_production_details(production_id):
    if not production_id:
        return pd.DataFrame().to_dict('records')

    if "db_session_id" not in session.keys():
        return pd.DataFrame().to_dict('records')

    db = get_database(session["db_session_id"])

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


def get_production_costs(production_id):
    if not production_id:
        return pd.DataFrame().to_dict('records')

    if "db_session_id" not in session.keys():
        return pd.DataFrame().to_dict('records')

    db = get_database(session["db_session_id"])

    transactions = {'main': db.transactions.find({'Production': ObjectId(production_id)})}

    if db.festivals.find_one({'_id': ObjectId(production_id)}):
        productions = db.productions.find({'festival': ObjectId(production_id)})
        for production in productions:
            transactions[production['title']] = db.transactions.find({'Production': ObjectId(production['_id'])})

    output = []
    total_amount = 0
    for title, costs in transactions.items():
        for cost in costs:
            if not cost.get('Recipient'):
                recipient = None
            elif type(cost['Recipient']) == str:
                recipient = cost['Recipient']
            else:
                recipient = db.people.find_one({'_id': cost['Recipient']})
                if not recipient:
                    recipient = db.productions.find_one({'_id': cost['Recipient']})
                    if not recipient:
                        recipient = db.festivals.find_one({'_id': cost['Recipient']})
                    recipient = recipient['title'] if recipient else None
                else:
                    recipient = f"{recipient['first_name']} {recipient['surname']}"

            total_amount += float(str(cost['Amount']))
            output.append(
                {
                    'reference': cost['Reference'],
                    'date': cost['Date'].date().strftime('%d %B %Y'),
                    'amount': str(cost['Amount']),
                    'recipient': recipient,
                    'description': cost['Description'] if title == 'main' else f"{cost['Description']} ({title})",
                }
            )
            
    if len(output) == 0:
        return pd.DataFrame().to_dict('records')

    output.append({'date': 'Total', 'amount': round(total_amount, 2)})

    return pd.DataFrame(output).sort_values('reference').to_dict('records')


def insert_production(p_type, name, venue, author, open, close, festival_id):
    if not has_request_context():
        return ""

    if p_type == 'Production' and (not name or not (festival_id or (open and close))):
        return "Title and either performance dates or festival are required"

    if p_type == 'Festival' and (not name or not open or not close):
        return "Title and performance dates are required"

    production_payload = {'title': name}
    if festival_id:
        if p_type == 'Festival':
            return "A festival cannot be part of another festival"

        try:
            festival_id = ObjectId(festival_id)
        except Exception as e:
            return f"Invalid festival ID: {e}"

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

    db = get_database(session["db_session_id"])

    collection = db.festivals if p_type == 'Festival' else db.productions

    if collection.find_one(production_filter):
        return "Production or Festival already exists"

    if venue:
        if festival_id:
            return "Venue can only be set by the festival"
        production_payload['venue'] = venue
    if author:
        if p_type == 'Festival':
            return "Only a production can have an author"
        production_payload['author'] = author

    new_production = collection.insert_one(production_payload)

    return f"New production: {str(new_production.inserted_id)}"


def update_production(production_id, venue, author, open_date, close_date, festival_id):
    if not has_request_context():
        return ""

    if not production_id:
        return "Person ID is required."

    try:
        production_id = ObjectId(production_id)
    except Exception as e:
        return f"Invalid production ID: {e}"

    if festival_id:
        try:
            festival_id = ObjectId(festival_id)
        except Exception as e:
            return f"Invalid festival ID: {e}"

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

    db = get_database(session["db_session_id"])

    result = db.productions.update_one({'_id': production_id}, update_payload)
    if result.modified_count == 0:
        return "Production not found or no data changes"

    return "Production updated successfully"


def delete_production(production_id):
    if not has_request_context():
        return ""

    if not production_id:
        return "Production ID is required"

    try:
        production_id = ObjectId(production_id)
    except Exception as e:
        return f"Invalid person ID: {e}"

    db = get_database(session["db_session_id"])

    if find_collection_link(production_id, db.transactions, 'Production'):
        return "Production cannot be deleted - link to Transactions"
    if find_collection_link(production_id, db.castcrew, 'production'):
        return "Production cannot be deleted - link to Cast & Crew"
    if find_collection_link(production_id, db.productions, 'festival'):
        return "Festival cannot be deleted - link to Productions"

    result = db.productions.delete_one({'_id': production_id})
    if result.deleted_count == 0:
        result = db.festivals.delete_one({'_id': production_id})
    if result.deleted_count == 0:
        return "Production or Festival not found"

    return "Production or Festival deleted successfully"
