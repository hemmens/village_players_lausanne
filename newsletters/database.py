import pandas as pd

from flask import has_request_context, session

from database import convert_date, get_database


def get_newsletters_list():
    if not has_request_context():
        return []

    db = get_database(session["db_session_id"])

    newsletters = pd.DataFrame(db.newsletters.find({})).sort_values('sent', ascending=False)

    newsletters = list(
        {
            'label': entry['sent'].strftime('%B %Y'),
            'value': entry['url'],
        }
        for entry in newsletters.to_dict('records')
    )
    return newsletters


def insert_newsletter(sent_date, url):
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

    new_newsletter = db.newsletters.insert_one(newsletters_payload)

    return f"New newsletter uploaded: {str(new_newsletter.inserted_id)}"
