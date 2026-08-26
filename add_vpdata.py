from datetime import datetime, timedelta

from bson.objectid import ObjectId
from pymongo.synchronous.collection import Collection

import vp_tools as vpt

def add_balance(
    balances: Collection,
    new_balance: float | None,
    month: int | None,
    year: int | None
) -> str:
    if not new_balance or not month or not year:
        return "Missing key data"

    balance_date = (datetime(year, month, 15) + timedelta(30)).replace(day=1) - timedelta(0, 60)

    if balances.find_one({'date': balance_date}):
        return "Balance data already exists for this month"

    new_item = balances.insert_one(
        {
            'date': balance_date,
            'balance': vpt.handle_decimal(new_balance),
        }
    )

    return f"New balance item: {str(new_item.inserted_id)}"

def add_festival(
    festivals: Collection,
    title: str | None,
    venue: str | None,
    open: str | None,
    close: str | None
) -> str:
    if not title or not open:
        return "Missing key data"

    if festivals.find_one({'title': title}):
        return "Festival name already exists"

    festival_payload = {
        'title': title,
        'open_date': vpt.convert_date(open),
    }

    if venue: 
        festival_payload['venue'] = venue
    if close:
        festival_payload['close_date'] = vpt.convert_date(close)

    new_festival = festivals.insert_one(festival_payload)

    return f"New festival: {str(new_festival.inserted_id)}"

def add_production(
    productions: Collection,
    title: str | None,
    venue: str | None,
    author: str | None,
    open: str | None,
    close: str | None,
    festival: str | None
) -> str:
    if not title or (not open and not festival):
        return "Missing key data"

    production_payload = {
        'title': title
    }

    if productions.find_one(production_payload):
        return "Production name already exists"

    if festival:
        production_payload['festival'] = ObjectId(festival)
    else:
        if venue: 
            production_payload['venue'] = venue
        if close:
            production_payload['close_date'] = vpt.convert_date(close)

    if author: 
        production_payload['author'] = author

    new_production = productions.insert_one(production_payload)

    return f"New production: {str(new_production.inserted_id)}"

def add_cast_crew(
    cast_crew: Collection,
    person: str | None,
    production: str | None,
    role: str | None,
    name: str | None
) -> str:
    if not person or not production or not role:
        return "Missing key data"

    cast_crew_payload = {
        'person': ObjectId(person),
        'production': ObjectId(production),
        'role': role.lower()
    }
    if cast_crew.find_one(cast_crew_payload):
        return "Cast/Crew member already exists"

    if name: 
        cast_crew_payload['role_name'] = name

    new_cast_crew = cast_crew.insert_one(cast_crew_payload)

    return f"New cast/crew: {str(new_cast_crew.inserted_id)}"

def add_committee(
    committee: Collection,
    person: str | None,
    season: str | None,
    position: str | None
) -> str:
    if not person or not season or not position:
        return "Missing key data"

    committee_payload = {
        'person': ObjectId(person),
        'season': season,
        'position': position.lower()
    }

    if committee.find_one(committee_payload):
        return "Committee member already exists"

    new_committee = committee.insert_one(committee_payload)

    return f"New committee member: {str(new_committee.inserted_id)}"

def add_person(
    people: Collection,
    first_name: str | None,
    surname: str | None,
    address: str | None,
    postcode: str | None,
    address_private: bool | None,
    phone: str | None,
    phone_private: bool | None,
    mobile: str | None,
    mobile_private: bool | None,
    email: str | None,
    email_private: bool | None,
    gender: str | None,
    gdpr: str | None
) -> str:
    if not first_name or not surname:
        return "Missing key data"

    person_payload = {
        'first_name': first_name,
        'surname': surname
    }

    if people.find_one(person_payload):
        return "Person name already exists"

    if address:
        person_payload['address'] = address
    if postcode:
        person_payload['postcode'] = postcode
    if address_private:
        person_payload['address_private'] = address_private
    if phone:
        person_payload['home_phone'] = phone
    if phone_private:
        person_payload['home_phone_private'] = phone_private
    if mobile:
        person_payload['mobile'] = mobile
    if mobile_private:
        person_payload['mobile_private'] = mobile_private
    if email:
        person_payload['email'] = email
    if email_private:
        person_payload['email_private'] = email_private
    if gender:
        person_payload['gender'] = gender.lower()
    if gdpr:
        person_payload['gdpr'] = vpt.convert_date(gdpr)

    new_person = people.insert_one(person_payload)

    return f"New person: {str(new_person.inserted_id)}"
