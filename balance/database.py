import pandas as pd
from datetime import datetime, timedelta

from flask import has_request_context, session

from database import convert_date, get_database, handle_decimal


def get_balance(months, years, start_date, end_date):
    if not has_request_context():
        return []

    db = get_database(session["db_session_id"])

    query = {}
    if start_date:
        query['date'] = {'$gte': convert_date(start_date)}
    if end_date:
        if query.get('date'):
            query['date']['$lt'] = convert_date(end_date)
        else:
            query['date'] = {'$lt': convert_date(end_date)}

    balance = pd.DataFrame(db.balance.find(query)).sort_values('date')
    balance['month'] = balance.date.apply(lambda x: x.month)
    balance['year'] = balance.date.apply(lambda x: x.year)
    if months:
        balance = balance[balance.month.isin(months)]
    if years:
        balance = balance[balance.year.isin(years)]

    balance['amount'] = balance.balance.astype(str).astype(float)
    balance['difference'] = balance.amount - balance.amount.shift(1)
    balance = balance[['month', 'year', 'amount', 'difference']]

    balance.month = balance.month.map({
        1: 'January', 2: 'February', 3: 'March', 4: 'April', 5: 'May', 6: 'June', 7: 'July',
        8: 'August', 9: 'September', 10: 'October', 11: 'November', 12: 'December'
    })
    for col in ['amount', 'difference']:
        balance[col] = balance[col].apply(lambda x: f'{x:.2f}')

    return balance.to_dict('records')


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
