import pandas as pd
import re

from bson.objectid import ObjectId
from flask import has_request_context, session

from database import convert_date, get_database
from variables import GD_ID_REGEX


def get_newsletters_list():
    if not has_request_context():
        return []

    db = get_database(session["db_session_id"])

    newsletters = pd.DataFrame(db.newsletters.find({}))
    if newsletters.empty or 'sent' not in newsletters.columns or 'url' not in newsletters.columns:
        return []
    
    newsletters.sort_values('sent', ascending=False, inplace=True)

    url_template = 'https://drive.google.com/file/d/{{FILEID}}/preview'
    newsletters['file_id'] = newsletters.url.apply(lambda url: re.findall(GD_ID_REGEX, url))
    newsletters.file_id = newsletters.file_id.apply(lambda x: x[0] if bool(x) else '')
    newsletters.url = newsletters.file_id.apply(
        lambda x: url_template.replace('{{FILEID}}', x) if bool(x) else None
    )
    if 'name' not in newsletters.columns:
        newsletters['name'] = pd.NA

    newsletters = list(
        {
            'label': (
                entry['sent'].strftime('%B %Y') if pd.isna(entry['name']) else entry['name']
            ),
            'value': f"{entry['_id']} || {entry['url']}",
        }
        for entry in newsletters.to_dict('records')
    )
    return newsletters


def insert_newsletter(sent_date, url, name):
    if not has_request_context():
        return ""

    if not sent_date or not url:
        return "Date and URL are required"
    
    db = get_database(session["db_session_id"])

    newsletters_payload = {'sent': convert_date(sent_date)}

    if db.newsletters.find_one(newsletters_payload):
        return "Newsletter date already exists"

    if db.newsletters.find_one({'url': url}):
        return "Newsletter URL already in use"

    newsletters_payload['url'] = url
    if bool(name):
        newsletters_payload['name'] = name

    new_newsletter = db.newsletters.insert_one(newsletters_payload)

    return f"New newsletter uploaded: {str(new_newsletter.inserted_id)}"


def update_newsletter(selected_id, sent_date, url, name):
    if not has_request_context():
        return ""

    newsletter_id = selected_id.split(' || ')[0] if selected_id else None

    if not newsletter_id:
        return "Newsletter ID is required"

    try:
        newsletter_id = ObjectId(newsletter_id)
    except Exception as e:
        return f"Invalid newsletter ID: {e}"

    if not sent_date or not url:
        return "Date and URL are required"

    update_payload = {
        '$set': {
            'sent': convert_date(sent_date),
            'url': url
        },
        '$unset': {}
    }

    if name:
        update_payload['$set']['name'] = name
    else:
        update_payload['$unset']['name'] = ""
    
    db = get_database(session["db_session_id"])

    result = db.newsletters.update_one({'_id': newsletter_id}, update_payload)
    if result.modified_count == 0:
        return "Newsletter not found or no data changes"

    return "Newsletter updated successfully"
