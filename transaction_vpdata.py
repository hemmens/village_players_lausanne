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

    return f"Misc: New transaction: {str(new_transaction.inserted_id)}"

def add_renew_transaction(
    transactions: Collection,
    members: Collection,
    transaction_date: str,
    member_type: str,
    amount: float,
    renewers: list[str]
) -> str:
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
        new_member = members.insert_one(
            {
                'type': member_type,
                'season': f'20{SEASON-1}-{SEASON}',
                'person': person_id,
                'payment': new_transaction.inserted_id,
                'carry_over': False,
            }
        )
        renewed_ids.append(str(new_member.inserted_id))

    return f"Renew: New transaction: {str(new_transaction.inserted_id)}; New members: " + ', '.join(renewed_ids) 

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
        new_person = people.insert_one(
            {
                'first_name': person['first_name'],
                'surname': person['surname'],
                'email_private': True,
            }
        )
        person_ids.append(str(new_person.inserted_id))

        new_member = members.insert_one(
            {
                'type': member_type,
                'season': f'20{SEASON-1}-{SEASON}',
                'person': new_person.inserted_id,
                'payment': new_transaction.inserted_id,
                'carry_over': False,
            }
        )
        member_ids.append(str(new_member.inserted_id))

    return f"New: New transaction: {str(new_transaction.inserted_id)}; New people: {', '.join(person_ids)}; New members: {', '.join(member_ids)}" 

def add_storage_cost(
    transactions: Collection,
    transaction_date: str,
    amount: float,
    recipient_text: str
) -> str:
    new_item = transactions.insert_one(
        {
            'Reference': vpt.get_new_ref(transactions, SEASON),
            'Date': vpt.convert_date(transaction_date),
            'Amount': vpt.handle_decimal(amount),
            'Type': 'Storage',
            'Recipient': recipient_text
        }
    )

    return f"Storage: New storage item: {str(new_item.inserted_id)}"

def add_bank_charge(
    transactions: Collection,
    transaction_date: str,
    amount: float
) -> str:
    new_item = transactions.insert_one(
        {
            'Reference': vpt.get_new_ref(transactions, SEASON),
            'Date': vpt.convert_date(transaction_date),
            'Amount': vpt.handle_decimal(amount),
            'Type': 'Bank Charges'
        }
    )

    return f"Bank Charge: New bank charge: {str(new_item.inserted_id)}"
