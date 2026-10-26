from datetime import datetime, timedelta

from flask import has_request_context, session

from database import get_database, handle_decimal

def insert_balance(amount, month, year):
    if not has_request_context():
        return ""

    if not amount or not month or not year:
        return "Month and Amount required"

    date = datetime(year, month, 25, 23, 59)
    date += timedelta(10)
    date = date.replace(day=1) - timedelta(1)

    balance_payload = {'date': date}
    
    db = get_database(session["db_session_id"])

    if db.balance.find_one(balance_payload):
        return "Balance month already exists"

    balance_payload['balance'] = handle_decimal(amount)
    new_balance = db.balance.insert_one(balance_payload)

    return f"New balance: {str(new_balance.inserted_id)}"
