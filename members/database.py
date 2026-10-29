import pandas as pd
from Levenshtein import ratio

from bson.objectid import ObjectId
from flask import has_request_context, session

from database import get_database
from variables import MEMBER_LIST_COLUMNS

NO_MEMBER_MESSAGE = """
No member found. Email checks are more reliable, if you haven't tried that already. \n
If you know you've been a member before, consider checking earlier seasons first to \n
make sure we're checking your details correctly. Finally, you can contact \n
info@villageplayers.ch if you have any questions.
"""
SORT_COLUMNS = ['season', 'surname']

def get_member_list(role, seasons, types, persons, columns):
    if not has_request_context() or role not in {"Committee", "Treasurer", "Public"}:
        return pd.DataFrame().to_dict('records')

    if "db_session_id" not in session.keys():
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


def get_member_check(first_name, surname, email, season):
    if not has_request_context():
        return None

    if not season:
        return "Season is required"

    if not first_name or not surname:
        return "Please provide both names"

    db = get_database(session["db_session_id"])

    people = pd.DataFrame(db.people.find({})).set_index('_id')
    members = pd.DataFrame(db.members.find({'season': season}))
    members = members.join(people, 'person')
    if members.shape[0] == 0:
        return "Error retrieving database information"

    members['full_name'] = members.apply(
        lambda row: (f"{row.first_name} {row.surname}").strip().lower(), axis=1
    )
    check_name = (f"{first_name} {surname}").strip().lower()
    members['ratio'] = members.full_name.apply(lambda x: ratio(x, check_name))
    members.sort_values('ratio', ascending=False, inplace=True)
    member = members.iloc[0]
    if member.ratio >= 0.8:
        return f"{member.full_name.title()} is a {season} member"

    if email:
        members = members[members.email == email]
        if members.shape[0] == 0:
            return "No members with this email address were found"

        members = members[['full_name', 'email', 'ratio']]
        members.drop_duplicates(inplace=True)

        if members.shape[0] >= 2:
            return """
                    Multiple members found with the same email address.
                    Please contact info@villageplayers.ch.
                """

        member = members.iloc[0]
        if member.ratio >= 0.5:
            return f"{member.full_name.title()} is a {season} member"
        else:
            return """
                    This email matches a member but the provided name does not.
                    Please contact info@villageplayers.ch.
                """

    return "Please provide an email address for additional verification"
