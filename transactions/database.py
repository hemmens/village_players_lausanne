from bson.objectid import ObjectId
from flask import session

from database import convert_date, extract_name, get_database, get_new_ref, handle_decimal

def insert_misc_transaction(t_type, date, amount, description, recipient, recipient_text, production_id):
    db = get_database(session["db_session_id"])
    payload = {
        'Reference': get_new_ref(convert_date(date)),
        'Date': convert_date(date),
        'Amount': handle_decimal(amount),
        'Type': t_type,
    }
    if recipient_text:
        payload['Recipient'] = recipient_text
    elif recipient:
        payload['Recipient'] = ObjectId(recipient.split('|')[0])
    if description:
        payload['Description'] = description
    if production_id:
        payload['Production'] = ObjectId(production_id)

    db.transactions.insert_one(payload)

    return f"New transaction: {payload['Reference']}"


def insert_renewing_member(date, amount, m_type, season, members):
    if not m_type or not season or not members:
        return "Type, Season and Name required"
    
    db = get_database(session["db_session_id"])

    member_ids = [ObjectId(m.split('|')[0]) for m in members]
    member_names = [m.split('|')[1] for m in members]

    transaction_payload = {
        'Reference': get_new_ref(convert_date(date)),
        'Date': convert_date(date),
        'Amount': handle_decimal(amount),
        'Type': 'Membership Subscription',
        'Description': ' & '.join(member_names),
    }

    message = f"New transaction: {transaction_payload['Reference']}"

    transaction_id = None
    for person_id in member_ids:
        member_payload = {
            'season': season,
            'person': person_id,
        }
        member = db.members.find_one(member_payload)
        if member:
            transaction_payload['existing_member'] = member['_id']
            if not transaction_id:
                new_transaction = db.transactions.insert_one(transaction_payload)
                transaction_id = new_transaction.inserted_id
        else:
            if not transaction_id:
                new_transaction = db.transactions.insert_one(transaction_payload)
                transaction_id = new_transaction.inserted_id
            member_payload['type'] = m_type
            member_payload['payment'] = new_transaction.inserted_id
            member_payload['carry_over'] = False

            new_member = db.members.insert_one(member_payload)
            message += f"; New member: {new_member.inserted_id}"

    return message


def insert_new_member(date, amount, m_type, season, new_1):
    name = extract_name(new_1)
    if not m_type or not season or not name:
        return "Type, Season and Name required"

    db = get_database(session["db_session_id"])

    transaction_payload = {
        'Reference': get_new_ref(convert_date(date)),
        'Date': convert_date(date),
        'Amount': handle_decimal(amount),
        'Type': 'Membership Subscription',
        'Description': name['full_name'],
    }

    message = f"New transaction: {transaction_payload['Reference']}"

    person_payload = {
        'first_name': name['first_name'],
        'surname': name['surname'],
    }
    person = db.people.find_one(person_payload)
    if person:
        person_id = person['_id']
    else:
        person_payload['email_private'] = True
        new_person = db.people.insert_one(person_payload)
        person_id = new_person.inserted_id
        message += f"; New person: {person_id}"

    member_payload = {
        'season': season,
        'person': person_id,
    }
    member = db.members.find_one(member_payload)
    if member:
        transaction_payload['existing_member'] = member['_id']
        new_transaction = db.transactions.insert_one(transaction_payload)
    else:
        new_transaction = db.transactions.insert_one(transaction_payload)
        member_payload['type'] = m_type
        member_payload['payment'] = new_transaction.inserted_id
        member_payload['carry_over'] = False

        new_member = db.members.insert_one(member_payload)
        message += f"; New member: {new_member.inserted_id}"

    return message


def insert_transaction(t_type, date, amount, description, recipient, recipient_text,
                        m_type, season, renew, new_1, production_id): # new_2, new_3, existing, 
    # if not has_request_context():
    #     return {"error": "No request context."}, 400

    if not t_type or not date or not amount:
        return "Type, Date, and Amount are required." # {"error": "Person, season, and position are required."}, 400

    if t_type == 'Membership Subscription':
        if new_1 and not renew:
            return insert_new_member(date, amount, m_type, season, new_1)
        elif not new_1 and renew:
            return insert_renewing_member(date, amount, m_type, season, renew)
    elif t_type in {'Production', "Entr'Acts", 'Materials', 'Subscriptions', 'Other'}:
        return insert_misc_transaction(
            t_type, date, amount, description, recipient, recipient_text, production_id
        )

    return "" # f"New Cast or Crew Member: {str(new_castcrew.inserted_id)}" # {"ok": True}, 201
