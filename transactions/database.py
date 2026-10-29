from bson.objectid import ObjectId
from flask import session

from database import convert_date, extract_name, get_database, get_new_ref, handle_decimal

def insert_member(date, amount, mbr_type, season, mbr_renew,
            mbr_new_1, mbr_new_2, mbr_new_3, mbr_existing):
    db = get_database(session["db_session_id"])
    transaction_payload = {
        'Reference': get_new_ref(convert_date(date)),
        'Date': convert_date(date),
        'Amount': handle_decimal(amount),
        'Type': 'Membership Subscription',
    }
    message = f"New transaction: {transaction_payload['Reference']}"
    person_ids = []
    full_names = []
    if bool(mbr_existing):
        member = db.members.find_one({'_id': ObjectId(mbr_existing)})
        if not bool(member):
            return "Selected member not found"

        person = db.people.find_one({'_id': member['person']})
        if not bool(person):
            return "Person connected to selected member not found"
        
        transaction_payload['Description'] = (
            f"{person['first_name']} {person['surname']} (extra payment)"
        )
        transaction_payload['Member'] = member['_id']
        new_transaction = db.transactions.insert_one(transaction_payload)
        if bool(new_transaction):
            return message
        else:
            return "Insert new transaction failed"
    elif not bool(mbr_type) or not bool(season):
        return "Provide membership type and season"
    elif bool(mbr_new_1):
        name_1 = extract_name(mbr_new_1)
        name_2 = extract_name(mbr_new_2) if bool(mbr_new_2) else None
        name_3 = extract_name(mbr_new_3) if bool(mbr_new_3) else None

        for name in [name_1, name_2, name_3]:
            if not bool(name):
                continue

            person_payload = {
                'first_name': name['first_name'],
                'surname': name['surname']
            }
            person = db.people.find_one(person_payload)
            if bool(person):
                person_ids.append(person['_id'])
            else:
                person_payload['email_private'] = True
                new_person = db.people.insert_one(person_payload)
                if bool(new_person):
                    person_ids.append(new_person.inserted_id)
                    message += f"; New person inserted: {name['full_name']}"
                else:
                    return f"New person {name['full_name']} could not be found or created"

            full_names.append(name['full_name'])

    if bool(mbr_renew):
        for person in mbr_renew:
            person_id, full_name = person.split('|')[:2]
            person_ids.append(ObjectId(person_id))
            full_names.append(full_name)

    if not bool(person_ids) or not bool(full_names):
        return "Please provide new member names"
    
    transaction_payload['Description'] = ' & '.join(full_names)

    new_transaction = db.transactions.insert_one(transaction_payload)
    if not bool(new_transaction):
        return "Insert new transaction failed"

    for person_id in person_ids:
        member_payload = {
            'person': person_id,
            'season': season,
            'type': mbr_type,
        }
        member = db.members.find_one(member_payload)
        if bool(member):
            message += "; Member already exists - not added"
        else:
            member_payload['payment'] = new_transaction.inserted_id
            member_payload['carry_over'] = False
            new_member = db.members.insert_one(member_payload)
            if bool(new_member):
                message += f"; New member {new_member.inserted_id}"
            else:
                message += f"; Failed to add new member"

    return message


def insert_misc_transaction(
    t_type, date, amount, description, recipient, recipient_text, production_id
):
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


def insert_storage(date, amount, recipient_text):
    if not date or not amount or not recipient_text:
        return "Date, Amount, and Recipient required"

    db = get_database(session["db_session_id"])

    transaction_payload = {
        'Reference': get_new_ref(convert_date(date)),
        'Date': convert_date(date),
        'Amount': handle_decimal(amount),
        'Type': 'Storage',
        'Description': recipient_text,
    }

    db.transactions.insert_one(transaction_payload)

    return f"New transaction: {transaction_payload['Reference']}"


def insert_bank_charge(date, amount):
    if not date or not amount:
        return "Date and Amount required"

    db = get_database(session["db_session_id"])

    transaction_payload = {
        'Reference': get_new_ref(convert_date(date)),
        'Date': convert_date(date),
        'Amount': handle_decimal(amount),
        'Type': 'Bank Charges',
    }

    db.transactions.insert_one(transaction_payload)

    return f"New transaction: {transaction_payload['Reference']}"


def insert_transaction(t_type, date, amount, description, recipient, recipient_text,
                        mbr_type, season, mbr_renew, mbr_new_1, mbr_new_2, mbr_new_3,
                        mbr_existing, production_id):
    if not t_type or not date or not amount:
        return "Type, Date, and Amount are required."

    if t_type == 'Membership Subscription':
        return insert_member(
            date, amount, mbr_type, season, mbr_renew,
            mbr_new_1, mbr_new_2, mbr_new_3, mbr_existing
        )
    elif t_type in {'Production', "Entr'Acts", 'Materials', 'Subscriptions', 'Other'}:
        return insert_misc_transaction(
            t_type, date, amount, description, recipient, recipient_text, production_id
        )
    elif t_type == 'Storage':
        return insert_storage(date, amount, recipient_text)
    elif t_type == 'Bank Charges':
        return insert_bank_charge(date, amount)

    return "Transaction Type not recognised"
