from bson.objectid import ObjectId
from pymongo.synchronous.collection import Collection

from config import SEASON
import vp_tools as vpt

def add_misc_transaction(
    transactions: Collection,
    transaction_type: str,
    transaction_date: str,
    amount: float,
    description: str | None,
    recipient: str | None,
    recipient_text: str | None,
    production: str | None
) -> str:
    if not transaction_date or not amount or not transaction_type:
        return "Missing key data"

    payload = {
        'Reference': vpt.get_new_ref(transactions, SEASON),
        'Date': vpt.convert_date(transaction_date),
        'Amount': vpt.handle_decimal(amount),
        'Type': transaction_type,
    }
    if recipient:
        payload['Recipient'] = ObjectId(recipient)
    if recipient_text:
        payload['Recipient'] = recipient_text
    if description:
        payload['Description'] = description
    if production:
        payload['Production'] = ObjectId(production)

    new_transaction = transactions.insert_one(payload)

    return f"New transaction: {str(new_transaction.inserted_id)}"

def add_renew_transaction(
    transactions: Collection,
    members: Collection,
    transaction_date: str,
    member_type: str,
    amount: float,
    renewers: list[str]
) -> str:
    if not transaction_date or not amount or not renewers:
        return "Missing key data"

    season = f'20{SEASON-1}-{SEASON}'
    new_transaction = transactions.insert_one(
        {
            'Reference': vpt.get_new_ref(transactions, SEASON),
            'Date': vpt.convert_date(transaction_date),
            'Amount': vpt.handle_decimal(amount),
            'Type': 'Membership Subscription',
            'Description': ' & '.join([x.split('|')[1] for x in renewers])
        }
    )

    renewer_ids = [ObjectId(x.split('|')[0]) for x in renewers]
    renewed_ids = []
    for person_id in renewer_ids:
        member_find = members.find_one(
            {'season': season, 'person': person_id}
        )
        if not member_find:
            new_member = members.insert_one(
                {
                    'type': member_type,
                    'season': season,
                    'person': person_id,
                    'payment': new_transaction.inserted_id,
                    'carry_over': False,
                }
            )
            renewed_ids.append(str(new_member.inserted_id))
        else:
            renewed_ids.append(f"{person_id} already in database")

    return f"New transaction: {str(new_transaction.inserted_id)}; New members: " + ', '.join(renewed_ids) 

def add_new_transaction(
    transactions: Collection,
    people: Collection,
    members: Collection,
    transaction_date: str,
    member_type: str,
    amount: float,
    member_1: str,
    member_2: str | None,
    member_3: str | None
) -> str:
    if not transaction_date or not amount or not member_1:
        return "Missing key data"

    season = f'20{SEASON-1}-{SEASON}'
    member_1 = vpt.extract_new_names(member_1)
    member_2 = vpt.extract_new_names(member_2)
    member_3 = vpt.extract_new_names(member_3)
    people_to_add = [member_1]
    description = member_1['full_name']
    if member_2 is not None:
        people_to_add.append(member_2)
        description += f" & {member_2['full_name']}"
        if member_3 is not None:
            people_to_add.append(member_3)
            description += f" & {member_3['full_name']}"

    new_transaction = transactions.insert_one(
        {
            'Reference': vpt.get_new_ref(transactions, SEASON),
            'Date': vpt.convert_date(transaction_date),
            'Amount': vpt.handle_decimal(amount),
            'Type': 'Membership Subscription',
            'Description': description
        }
    )

    person_ids = []
    member_ids = []
    for person in people_to_add:
        person_find = people.find_one(
            {name: person[name]} for name in ['first_name', 'surname']
        )
        if not person_find:
            new_person = people.insert_one(
                {
                    'first_name': person['first_name'],
                    'surname': person['surname'],
                    'email_private': True,
                }
            )
            person_id = new_person.inserted_id
            person_ids.append(str(person_id))
        else:
            person_id = person_find['_id']
            person_ids.append(f"{person['full_name']} already in database")

        member_find = members.find_one(
            {'season': season, 'person': person_id}
        )
        if not member_find:
            new_member = members.insert_one(
                {
                    'type': member_type,
                    'season': season,
                    'person': person_id,
                    'payment': new_transaction.inserted_id,
                    'carry_over': False,
                }
            )
            member_ids.append(str(new_member.inserted_id))
        else:
            member_ids.append(f"{person['full_name']} already in database")

    return f"New transaction: {str(new_transaction.inserted_id)}; New people: {', '.join(person_ids)}; New members: {', '.join(member_ids)}" 

def add_storage_cost(
    transactions: Collection,
    transaction_date: str,
    amount: float,
    recipient_text: str
) -> str:
    if not transaction_date or not amount or not recipient_text:
        return "Missing key data"

    new_item = transactions.insert_one(
        {
            'Reference': vpt.get_new_ref(transactions, SEASON),
            'Date': vpt.convert_date(transaction_date),
            'Amount': vpt.handle_decimal(amount),
            'Type': 'Storage',
            'Recipient': recipient_text
        }
    )

    return f"New storage item: {str(new_item.inserted_id)}"

def add_bank_charge(
    transactions: Collection,
    transaction_date: str,
    amount: float
) -> str:
    if not transaction_date or not amount:
        return "Missing key data"

    new_item = transactions.insert_one(
        {
            'Reference': vpt.get_new_ref(transactions, SEASON),
            'Date': vpt.convert_date(transaction_date),
            'Amount': vpt.handle_decimal(amount),
            'Type': 'Bank Charges'
        }
    )

    return f"New bank charge: {str(new_item.inserted_id)}"
