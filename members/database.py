import pandas as pd
from Levenshtein import ratio

from bson.objectid import ObjectId
from flask import has_request_context, session

from database import get_database
from variables import MEMBER_LIST_COLUMNS

SORT_COLUMNS = ['season', 'surname']


def return_member_types(members):
    types = members.type.to_list()
    if "Honorary" in types:
        return "Honorary"
    if "Full" in types:
        return "Full"
    return ", ".join(types)


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
        members = members[members.full_name == member.full_name]
        member_type = return_member_types(members)

        return f"{member.full_name.title()} is a {season} member ({member_type})"

    if member.ratio < 0.5:
        return "This name does not match any members for this season"

    if email:
        members = members[members.email == email]
        if members.shape[0] == 0:
            return "No members with this email address were found"

        member_dups = set(members.full_name.to_list())

        if len(member_dups) >= 2:
            return """
                    Multiple members found with the same email address.
                    Please contact info@villageplayers.ch.
                """

        member = members.iloc[0]
        if member.ratio >= 0.5:
            members = members[members.full_name == member.full_name]
            member_type = return_member_types(members)

            return f"{member.full_name.title()} is a {season} member ({member_type})"
        else:
            return """
                    This email matches a member but the provided name does not.
                    Please contact info@villageplayers.ch.
                """

    return "Please provide an email address for additional verification"


def insert_member(m_type, season, person):
    if not has_request_context():
        return ""

    if not m_type or not season or not person:
        return "Type, season, and person are required"

    person_id = person.split('|')[0]
    try:
        person_id = ObjectId(person_id)
    except Exception as e:
        return f"Invalid person ID: {e}"

    member_payload = {
        'season': season,
        'person': person_id,
    }
    
    db = get_database(session["db_session_id"])

    if db.members.find_one(member_payload):
        return "Member already exists"

    if m_type == 'Honorary':
        member_payload['type'] = 'Honorary'
        member_payload['carry_over'] = False
    elif m_type == 'Carry Over':
        member_payload['type'] = 'Full'
        member_payload['carry_over'] = True
    else:
        return "Type not recognised"

    new_member = db.members.insert_one(member_payload)
    if bool(new_member):
        return f"New member {new_member.inserted_id}"

    return "Failed to add new member"
