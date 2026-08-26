from bson.objectid import ObjectId
from pymongo.synchronous.collection import Collection

import vp_tools as vpt

def delete_record(
    collection: Collection,
    db_id: str | None,
    checks: dict[Collection, str] | None = None
) -> str:
    if not db_id:
        return "No record selected"

    if checks:
        for check, field in checks.items():
            if check.find_one({field: ObjectId(db_id)}):
                return "Cannot delete due to dependent records"

    deleted_record = collection.find_one_and_delete({'_id': ObjectId(db_id)})

    return f"Record deleted: {str(deleted_record['_id'])}"

def update_balance(
    balances: Collection,
    balance_id: str | None,
    amount: float | None,
) -> str:
    if not balance_id:
        return "Select a record to update"

    if not amount:
        return "Missing key data"

    entry = balances.find_one_and_update(
        {'_id': ObjectId(balance_id)},
        {'$set': {'amount': vpt.handle_decimal(amount)}}
    )

    return f"Updated balance item: {str(entry['_id'])}"

def update_festival(
    festivals: Collection,
    festival_id: str | None,
    venue: str | None,
    open: str | None,
    close: str | None
) -> str:
    if not festival_id:
        return "Select a record to update"

    if not open:
        return "Missing key data"

    update_payload = {
        '$set': {
            'open_date': vpt.convert_date(open)
        },
        '$unset': {}
    }

    if venue:
        update_payload['$set']['venue'] = venue
    else:
        update_payload['$unset']['venue'] = ""

    if close:
        update_payload['$set']['close_date'] = vpt.convert_date(close)
    else:
        update_payload['$unset']['close_date'] = ""

    entry = festivals.find_one_and_update(
        {'_id': ObjectId(festival_id)}, update_payload
    )

    return f"Updated festival: {str(entry['_id'])}"

def update_production(
    productions: Collection,
    production_id: str | None,
    venue: str | None,
    author: str | None,
    open: str | None,
    close: str | None,
    festival: str | None
) -> str:
    if not production_id:
        return "Select a record to update"

    if not open and not festival:
        return "Missing key data"

    if festival:
        update_payload = {
            '$set': {
                'festival': ObjectId(festival)
            },
            '$unset': {
                'venue': "",
                'open_date': "",
                'close_date': "",
            }
        }
    else:
        update_payload = {
            '$set': {
                'open_date': vpt.convert_date(open)
            },
            '$unset': {
                'festival': ""
            }
        }

        if venue:
            update_payload['$set']['venue'] = venue
        else:
            update_payload['$unset']['venue'] = ""

        if close:
            update_payload['$set']['close_date'] = vpt.convert_date(close)
        else:
            update_payload['$unset']['close_date'] = ""

    if author:
        update_payload['$set']['author'] = author
    else:
        update_payload['$unset']['author'] = ""

    entry = productions.find_one_and_update(
        {'_id': ObjectId(production_id)}, update_payload
    )

    return f"Updated production: {str(entry['_id'])}"

def update_cast_crew(
    castcrew: Collection,
    cast_id: str | None,
    name: str | None,
) -> str:
    if not cast_id:
        return "Select a record to update"

    update_payload = {'$set': {'role_name': name}} if name else {'$unset': {'role_name': ""}}

    entry = castcrew.find_one_and_update(
        {'_id': ObjectId(cast_id)}, update_payload
    )

    return f"Updated cast / crew member: {str(entry['_id'])}"

def update_person(
    people: Collection,
    person_id: str | None,
    address: str | None,
    postcode: str | None,
    address_private: bool | None,
    home_phone: str | None,
    home_phone_private: bool | None,
    mobile: str | None,
    mobile_private: bool | None,
    email: str | None,
    email_private: bool | None,
    gender: str | None,
    gdpr: str | None
) -> str:
    if not person_id:
        return "Select a record to update"

    update_payload = {
        '$set': {},
        '$unset': {}
    }

    if address:
        update_payload['$set']['address'] = address
    else:
        update_payload['$unset']['address'] = ""

    if postcode:
        update_payload['$set']['postcode'] = postcode
    else:
        update_payload['$unset']['postcode'] = ""

    if address_private:
        update_payload['$set']['address_private'] = address_private
    else:
        update_payload['$unset']['address_private'] = ""

    if home_phone:
        update_payload['$set']['home_phone'] = home_phone
    else:
        update_payload['$unset']['home_phone'] = ""

    if home_phone_private:
        update_payload['$set']['home_phone_private'] = home_phone_private
    else:
        update_payload['$unset']['home_phone_private'] = ""

    if mobile:
        update_payload['$set']['mobile'] = mobile
    else:
        update_payload['$unset']['mobile'] = ""

    if mobile_private:
        update_payload['$set']['mobile_private'] = mobile_private
    else:
        update_payload['$unset']['mobile_private'] = ""

    if email:
        update_payload['$set']['email'] = email
    else:
        update_payload['$unset']['email'] = ""

    if email_private:
        update_payload['$set']['email_private'] = email_private
    else:
        update_payload['$unset']['email_private'] = ""

    if gender:
        update_payload['$set']['gender'] = gender
    else:
        update_payload['$unset']['gender'] = ""

    if gdpr:
        update_payload['$set']['gdpr'] = vpt.convert_date(gdpr)
    else:
        update_payload['$unset']['gdpr'] = ""

    entry = people.find_one_and_update(
        {'_id': ObjectId(person_id)}, update_payload
    )

    return f"Updated person: {str(entry['_id'])}"
