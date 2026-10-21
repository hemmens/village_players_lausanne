import pandas as pd

from bson.objectid import ObjectId
from flask import has_request_context, session

from database import get_database
from variables import MEMBER_LIST_COLUMNS

def get_member_list(role, seasons, types, persons, columns):
    db = get_database(session["db_session_id"])
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