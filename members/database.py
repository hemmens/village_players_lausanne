import pandas as pd

from bson.objectid import ObjectId
from flask import has_request_context, session

from database import get_database
from variables import MEMBER_LIST_COLUMNS

SORT_COLUMNS = ['season', 'surname']

def get_member_list(role, seasons, types, persons, columns):
    if not has_request_context() or role not in {"Committee", "Treasurer", "Public"}:
        return pd.DataFrame().to_dict('records')
    
    db = get_database(session["db_session_id"])

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
        if any(['Payment' in col for col in columns]):
            transactions = pd.DataFrame(
                db.transactions.find({'Type': 'Membership Subscription'})
            ).set_index('_id')[['Date', 'Amount', 'Member']]

            try:
                members = members.join(transactions, 'payment')
            except:
                pass

            extra_transactions = transactions[transactions['Member'].isin(members.index)]
            for et_id, et in extra_transactions.iterrows():
                member = members.loc[et.Member]
                member.Date = et.Date
                member.Amount = et.Amount
                members.loc[et_id] = member

        mcols = [
            MEMBER_LIST_COLUMNS.get(col) for col in columns
            if MEMBER_LIST_COLUMNS.get(col) in members.columns
        ]
        for col in SORT_COLUMNS:
            if col not in mcols:
                mcols.append(col)

        members = members[mcols]
        for col in ['gdpr', 'Amount', 'Date']:
            if col in members.columns:
                members[col] = members[col].astype(str)

    members.sort_values(SORT_COLUMNS, inplace=True)
    
    return members.to_dict('records')