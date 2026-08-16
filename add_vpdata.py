from datetime import datetime, timedelta

from pymongo.synchronous.collection import Collection

import vp_tools as vpt

def add_balance(
    balances: Collection,
    new_balance: float,
    month: int,
    year: int
) -> str:
    if not new_balance or not month or not year:
        return "Missing key data"

    balance_date = (datetime(year, month, 15) + timedelta(30)).replace(day=1) - timedelta(0, 60)

    new_item = balances.insert_one(
        {
            'date': balance_date,
            'balance': vpt.handle_decimal(new_balance),
        }
    )

    return f"New balance item: {str(new_item.inserted_id)}"
