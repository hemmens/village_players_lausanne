from bson.objectid import ObjectId
from flask import has_request_context, session

from database import convert_date, find_collection_link, get_database

def insert_person(first_name, surname, address, postcode, address_private, home_phone,
        home_phone_private, mobile, mobile_private, email, email_private, gender,
        gdpr, committee_email):
    # if not has_request_context():
    #     return {"error": "No request context."}, 400

    if not first_name or not surname:
        return "First name and surname are required." # {"error": "Person, season, and position are required."}, 400

    person_payload = {
        'first_name': first_name,
        'surname': surname
    }
    
    db = get_database(session["db_session_id"])

    if db.people.find_one(person_payload):
        return "Person already exists" # {"error": "Committee member already exists"}, 400

    if address:
        person_payload['address'] = address
    if postcode:
        person_payload['postcode'] = postcode
    if address_private:
        person_payload['address_private'] = (address_private == ['private'])
    if home_phone:
        person_payload['home_phone'] = home_phone
    if home_phone_private:
        person_payload['home_phone_private'] = (home_phone_private == ['private'])
    if mobile:
        person_payload['mobile'] = mobile
    if mobile_private:
        person_payload['mobile_private'] = (mobile_private == ['private'])
    if email:
        person_payload['email'] = email
    if email_private:
        person_payload['email_private'] = (email_private == ['private'])
    if gender:
        person_payload['gender'] = gender
    if gdpr:
        person_payload['gdpr'] = convert_date(gdpr)
    if committee_email:
        person_payload['committee_email'] = (
            committee_email if '@' in committee_email else f'{committee_email}@villageplayers.ch'
        )

    new_person = db.people.insert_one(person_payload)

    return f"New person: {str(new_person.inserted_id)}" # {"ok": True}, 201


def update_person(person_id, address, postcode, address_private, home_phone,
        home_phone_private, mobile, mobile_private, email, email_private, gender,
        gdpr, committee_email):
    if not has_request_context():
        return "" # {"error": "No request context."}, 400

    if not person_id:
        return "Person ID is required." # {"error": "Committee member ID is required."}, 400

    try:
        person_id = ObjectId(person_id)
    except Exception as e:
        return f"Invalid person ID: {e}" # {"error": f"Invalid committee member ID: {e}"}, 400

    update_payload = {
        '$set': {},
        '$unset': {}
    }
    
    db = get_database(session["db_session_id"])

    if address:
        update_payload['$set']['address'] = address
    else:
        update_payload['$unset']['address'] = ""

    if postcode:
        update_payload['$set']['postcode'] = postcode
    else:
        update_payload['$unset']['postcode'] = ""

    if address_private:
        update_payload['$set']['address_private'] = (address_private == ['private'])
    else:
        update_payload['$unset']['address_private'] = ""

    if home_phone:
        update_payload['$set']['home_phone'] = home_phone
    else:
        update_payload['$unset']['home_phone'] = ""

    if home_phone_private:
        update_payload['$set']['home_phone_private'] = (home_phone_private == ['private'])
    else:
        update_payload['$unset']['home_phone_private'] = ""

    if mobile:
        update_payload['$set']['mobile'] = mobile
    else:
        update_payload['$unset']['mobile'] = ""

    if mobile_private:
        update_payload['$set']['mobile_private'] = (mobile_private == ['private'])
    else:
        update_payload['$unset']['mobile_private'] = ""

    if email:
        update_payload['$set']['email'] = email
    else:
        update_payload['$unset']['email'] = ""

    if email_private:
        update_payload['$set']['email_private'] = (email_private == ['private'])
    else:
        update_payload['$unset']['email_private'] = ""

    if gender:
        update_payload['$set']['gender'] = gender
    else:
        update_payload['$unset']['gender'] = ""

    if gdpr:
        update_payload['$set']['gdpr'] = convert_date(gdpr)
    else:
        update_payload['$unset']['gdpr'] = ""

    if committee_email:
        update_payload['$set']['committee_email'] = (
            committee_email if '@' in committee_email else f'{committee_email}@villageplayers.ch'
        )
    else:
        update_payload['$unset']['committee_email'] = ""

    result = db.people.update_one({'_id': person_id}, update_payload)
    if result.modified_count == 0:
        return "Person not found or no data changes" # {"error": "Committee member not found"}, 404

    return "Person updated successfully" # {"ok": True}, 200


def delete_person(person_id):
    # if not has_request_context():
    #     return {"error": "No request context."}, 400

    if not person_id:
        return "Person ID is required." # {"error": "Committee member ID is required."}, 400

    try:
        person_id = ObjectId(person_id)
    except Exception as e:
        return f"Invalid person ID: {e}" # {"error": f"Invalid committee member ID: {e}"}, 400
    
    db = get_database(session["db_session_id"])

    if find_collection_link(person_id, db.members, 'person'):
        return "Person cannot be deleted - link to Members"
    if find_collection_link(person_id, db.transactions, 'Recipient'):
        return "Person cannot be deleted - link to Transactions"
    if find_collection_link(person_id, db.castcrew, 'person'):
        return "Person cannot be deleted - link to Cast & Crew"
    if find_collection_link(person_id, db.committee, 'holder'):
        return "Person cannot be deleted - link to Committee"

    result = db.people.delete_one({'_id': person_id})
    if result.deleted_count == 0:
        return "Person not found" # {"error": "Committee member not found"}, 404

    return "Person deleted successfully" # {"ok": True}, 200