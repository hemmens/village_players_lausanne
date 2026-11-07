import pandas as pd
import re
from datetime import date

from bson.objectid import ObjectId
from flask import session

from database import convert_date, extract_name, get_database, get_new_ref, handle_decimal


def get_recipients():
    db = get_database(session["db_session_id"])
    transactions = pd.DataFrame(db.transactions.find())
    people = pd.DataFrame(db.people.find()).set_index('_id')
    transactions = transactions.join(people, 'Recipient')
    transactions['label'] = transactions.apply(
        lambda row: (
            f"{row['first_name']} {row['surname']}"
            if pd.notnull(row['first_name']) and pd.notnull(row['surname'])
            else (
                row['Recipient']
                if type(row['Recipient']) == str
                else None
            )
        ), axis=1
    )
    transactions['value'] = transactions.apply(
        lambda row: (
            str(row['Recipient'])
            if (
                (pd.notnull(row['first_name']) and pd.notnull(row['surname']))
                or type(row['Recipient']) == str
            )
            else None
        ), axis=1
    )
    transactions = transactions[['label', 'value']].dropna().drop_duplicates().sort_values('label')
    return transactions.to_dict('records')


def get_transactions(t_type, start_date, end_date, recipient, production):
    transaction_filter = {}
    
    if t_type:
        transaction_filter['Type'] = {'$in': t_type}
    if start_date:
        transaction_filter['Date'] = {'$gte': convert_date(start_date)}
    if end_date:
        transaction_filter['Date'] = transaction_filter.get('Date', {})
        transaction_filter['Date']['$lte'] = convert_date(end_date)
    if recipient:
        recipients = [
            ObjectId(r) if re.fullmatch(r"[0-9a-f]{24}", r) is not None else r
            for r in recipient
        ]
        transaction_filter['Recipient'] = {'$in': recipients}
    if production:
        productions = [ObjectId(p) for p in production]
        transaction_filter['Production'] = {'$in': productions}

    db = get_database(session["db_session_id"])
    transactions = pd.DataFrame(db.transactions.find(transaction_filter))
    if transactions.empty:
        return pd.DataFrame().to_dict('records')

    transactions.Amount = transactions.Amount.astype(str)
    transactions.Date = transactions.Date.apply(lambda d: d.strftime("%d %B %Y"))
    for col in ['Recipient', 'Production']:
        if col not in transactions.columns:
            transactions[col] = None

    people = pd.DataFrame(db.people.find()).set_index('_id')
    productions = pd.DataFrame(db.productions.find()).set_index('_id')
    festivals = pd.DataFrame(db.festivals.find()).set_index('_id')
    transactions = transactions.join(people, 'Recipient')
    transactions = transactions.join(productions, 'Recipient')
    transactions = transactions.join(festivals, 'Recipient', rsuffix='_festival')
    transactions['Recipient'] = transactions.apply(
        lambda row: (
            f"{row['first_name']} {row['surname']}"
            if pd.notnull(row['first_name']) and pd.notnull(row['surname'])
            else (
                row['title']
                if pd.notnull(row['title'])
                else (
                    row['title_festival']
                    if pd.notnull(row['title_festival'])
                    else row['Recipient']
                )
            )
        ), axis=1
    )

    transactions = transactions[['Type', 'Reference', 'Date', 'Amount', 'Description', 'Recipient', 'Production']]
    transactions = transactions.join(productions, 'Production')
    transactions = transactions.join(festivals, 'Production', rsuffix='_festival')
    transactions['Production'] = transactions.apply(
        lambda row: (
            row['title']
            if pd.notnull(row['title'])
            else (
                row['title_festival']
                if pd.notnull(row['title_festival'])
                else row['Production']
            )
        ), axis=1
    )

    transactions = transactions[['Type', 'Reference', 'Date', 'Amount', 'Description', 'Recipient', 'Production']]
    transactions.sort_values('Reference', ascending=False, inplace=True)
    if any([bool(t) for t in [t_type, start_date, end_date, recipient, production]]):
        transactions = pd.concat(
            [
                transactions,
                pd.DataFrame(
                    [['Total:', str(transactions.Amount.astype(float).sum().round(2))]],
                    columns=['Type', 'Amount']
                )
            ],
            ignore_index=True
        )
    return transactions.to_dict('records')


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
        'Recipient': recipient_text,
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
