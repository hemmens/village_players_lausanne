from datetime import datetime
import pandas as pd

from bson.decimal128 import Decimal128
from pymongo.synchronous.collection import Collection

def convert_date(date_str: str) -> datetime:
    transaction_date = date_str.split('-')
    return datetime(
        int(transaction_date[0]), int(transaction_date[1]), int(transaction_date[2])
    )

def get_new_ref(dataset: Collection, season: int):
    latest_refs = [
        x['Reference'] for x in dataset.find({'Reference': {'$gt': season*1000}})
    ]

    if len(latest_refs):
        return max(latest_refs) + 1
    else:
        return season*1000 + 1

def extract_new_names(name: str | None) -> dict[str, str] | None:
    if name is None:
        return None

    name_split = name.split(',')
    first_name = name_split[1].strip()
    surname = name_split[0].strip()
    full_name = first_name + ' ' + surname
    return {
        'first_name': first_name,
        'surname': surname,
        'full_name': full_name,
    }

def handle_decimal(amount: float) -> str:
    if (100 * amount) % 100 == 0:
        return Decimal128('%i' % amount)
    else:
        return Decimal128('%.2f' % amount)

def handle_status_message(tab: str, message: str) -> str:
    header = tab.split('-')[2:]
    header = ' '.join(header).title()
    return f"{header}: {message}"

def convert_objid_to_str(column: pd.Series) -> pd.Series:
    return column.apply(lambda x: str(x))

def get_productions_list(
    productions: Collection,
    festivals: Collection
) -> list[dict[str, str]]:
    ps = productions.find({})
    fs = festivals.find({})

    fs = {
        str(f['_id']): {
            'title': f['title'],
            'date': f['open_date'],
        }
    for f in fs}
    ps = {
        str(p['_id']): {
            'title': p['title'],
            'date': p['open_date'] if p.get('open_date') else fs[str(p['festival'])]['date'],
        }
    for p in ps}

    shows = pd.concat([
        pd.DataFrame.from_dict(fs, orient='index'),
        pd.DataFrame.from_dict(ps, orient='index')
    ])
    shows.sort_values('date', ascending=False, inplace=True)
    shows['label'] = shows.apply(
        lambda row: {'label': f"{row.title} ({row.date.year})", 'value': row.index}, axis=1
    )

    return shows['label'].to_list()
