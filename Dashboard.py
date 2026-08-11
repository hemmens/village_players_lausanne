from datetime import datetime, timedelta

from dash import Dash, html, dcc, callback, Output, Input, State
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import dash_ag_grid as dag

from config import BANK_CHARGE, MEMBER_TYPES, NOT_OK, OK, SEASONS, STORAGE_COST, STORAGE_OWNER, TRANS_TYPES, URI
import find_vpdata as fvp
import vp_tools as vpt
import write_vpdata as wvp

client = MongoClient(URI, server_api=ServerApi('1'))
db = client.myDatabase
NAMES = [
    {
        'label': f"{x['surname']}, {x['first_name']}",
        'value': str(x['_id']) + '|' + x['first_name'] + ' ' + x['surname'],
    }
    for x in db.people.find({})
]
PRODUCTIONS = [
    {
        'label': f"{x['title']} ({x['open_date'].year})",
        'value': str(x['_id']),
    }
    for x in db.productions.find({})
]
VERIFICATION = [
    {'label': OK, 'value': True},
    {'label': NOT_OK, 'value': False},
]
fields = {
    'transaction-type': {'type': 'dropdown', 'options': TRANS_TYPES},
    'membership-type': {'type': 'dropdown', 'options': MEMBER_TYPES},
    'date': {'type': 'date'},
    'amount': {'type': 'number'},
    'description': {'type': 'text'},
    'recipient': {'type': 'dropdown', 'options': NAMES},
    'recipient-text': {'type': 'text'},
    'member': {'type': 'dropdown-multi', 'options': NAMES},
    'member-1': {'type': 'text'},
    'member-2': {'type': 'text'},
    'member-3': {'type': 'text'},
    'production': {'type': 'dropdown', 'options': PRODUCTIONS},
    'month': {'type': 'number'},
    'year': {'type': 'number'},
    'season': {'type': 'dropdown-multi', 'options': SEASONS},
    'membership-type-find': {'type': 'dropdown-multi', 'options': MEMBER_TYPES},
    'verify': {'type': 'dropdown', 'options': VERIFICATION},
}
tab_values = {
    'tab-transaction': {
        'label': "Add Transaction",
        'defaults': {
            'transaction-type': None,
            'date': datetime.today().date(),
            'amount': None,
            'description': None,
            'recipient': None,
            'recipient-text': None,
        },
    },
    'tab-renew': {
        'label': "Add Renewing Member(s)",
        'defaults': {
            'membership-type': 'Full',
            'date': datetime.today().date(),
            'amount': 95,
            'member': None,
        },
    },
    'tab-new': {
        'label': "Add New Member(s)",
        'defaults': {
            'membership-type': 'Full',
            'date': datetime.today().date(),
            'amount': 95,
            'member-1': None,
            'member-2': None,
            'member-3': None,
        },
    },
    'tab-mixed': {
        'label': "Add Mixed New/Renewing Members",
        'keep': [
            'membership-type', 'date', 'amount',
            'member', 'member-1', 'member-2', 'member-3'
        ],
        'defaults': {
            'membership-type': 'Full',
            'date': datetime.today().date(),
            'amount': None,
            'member': None,
            'member-1': None,
            'member-2': None,
            'member-3': None,
        },
    },
    'tab-storage': {
        'label': "Add Storage",
        'defaults': {
            'transaction-type': 'Storage',
            'date': datetime.today().date().replace(day=1) - timedelta(1),
            'amount': STORAGE_COST,
            'recipient-text': STORAGE_OWNER,
        },
    },
    'tab-bank-charge': {
        'label': "Add Bank Charge",
        'defaults': {
            'transaction-type': 'Bank Charges',
            'date': datetime.today().date().replace(day=1) - timedelta(1),
            'amount': BANK_CHARGE,
        },
    },
    'tab-balance': {
        'label': "Add Balance Value",
        'defaults': {
            'amount': None,
            'month': (datetime.today().date().replace(day=1) - timedelta(1)).month,
            'year': (datetime.today().date().replace(day=1) - timedelta(1)).year,
        },
    },
    'tab-membership-list': {
        'label': "Show Members",
        'defaults': {
            'season': SEASONS[-1],
            'membership-type-find': MEMBER_TYPES,
        },
    },
}

app_layout = [
    html.H1('Village Players Database'),
    dcc.Tabs(
        id='tabs-access-data', value=list(tab_values.keys())[0], children=[
            dcc.Tab(label=layout['label'], value=tab)
            for tab, layout in tab_values.items()
        ]
    )
]

for field, layout in fields.items():
    app_layout.append(
        html.Div([
            field.replace('-', ' ').title() + ": ",
            (
                dcc.Input(id=field, type=layout['type']) if layout['type'] in ['text', 'number']
                else (
                    dcc.Dropdown(
                        id=field, options=layout['options'], multi=('multi' in layout['type'])
                    ) if 'dropdown' in layout['type']
                    else (
                        dcc.DatePickerSingle(id=field) if layout['type'] == 'date'
                        else ""
                    )
                )
            )
        ],
        id=f'div-{field}')
    )

app_layout.append(
    html.Div([
        html.Div(id='returned'),
    ])
)
app_layout.append(
    html.Div([
        dag.AgGrid(
            id='dataframe',
            rowData=[],
            columnDefs=[
                {'field': 'season'},
                {'field': 'type'},
                {'field': 'surname'},
                {'field': 'first_name', 'headerName': 'First Name'},
                {'field': 'email'},
            ],
        )
    ])
)

app = Dash(__name__)

app.layout = html.Div(app_layout)

@callback(
    Output('verify', 'value'),
    Input('tabs-access-data', 'value')
)
def falsify_on_tab_switch(tab: str):
    return False

# @callback(
#     Output('dataframe', 'columnDefs'),
#     Input('tabs-access-data', 'value')
# )
# def reset_columns_on_tab_switch(tab: str):
#     return []

def update_div(field):
    @callback(
        Output(f'div-{field}', 'hidden'),
        Input('tabs-access-data', 'value')
    )
    def hide_transaction_type(tab: str):
        return not field in tab_values[tab]['defaults'].keys()

    @callback(
        Output(field, 'date' if fields[field]['type'] == 'date' else 'value'),
        Input('tabs-access-data', 'value')
    )
    def hide_transaction_type(tab: str):
        return tab_values[tab]['defaults'].get(field)

for field in fields.keys():
    if field != 'verify':
        update_div(field)

@callback(
    Output('returned', 'children'),
    Input('verify', 'value'),
    State('tabs-access-data', 'value'),
    State('transaction-type', 'value'),
    State('membership-type', 'value'),
    State('date', 'date'),
    State('amount', 'value'),
    State('description', 'value'),
    State('recipient', 'value'),
    State('recipient-text', 'value'),
    State('member', 'value'),
    State('member-1', 'value'),
    State('member-2', 'value'),
    State('member-3', 'value'),
    State('production', 'value'),
    State('month', 'value'),
    State('year', 'value')
)
def return_status(
    verified: bool,
    tab: str,
    t_type: str | None,
    m_type: str | None,
    date: str | None,
    amount: float | None,
    description: str | None,
    recipient: str | None,
    recipient_text: str | None,
    member: list[str] | None,
    member_1: str | None,
    member_2: str | None,
    member_3: str | None,
    production: str | None,
    month: int | None,
    year: int | None
) -> str:
    if not verified:
        try:
            client.admin.command('ping')
            return vpt.handle_status_message(tab, "Ping successful!")
        except Exception as e:
            return vpt.handle_status_message(tab, e)

    if tab == 'tab-transaction':
        return vpt.handle_status_message(
            tab, wvp.add_misc_transaction(
                db.transactions, t_type, date, amount, description, recipient, recipient_text
            )
        )
    elif tab == 'tab-renew':
        return vpt.handle_status_message(
            tab, wvp.add_renew_transaction(
                db.transactions, db.members, date, m_type, amount, member
            )
        )
    elif tab == 'tab-new':
        return vpt.handle_status_message(
            tab, wvp.add_new_transaction(
                db.transacations, db.people, db.members, date, m_type, amount,
                member_1, member_2, member_3
            )
        )
    elif tab == 'tab-storage':
        return vpt.handle_status_message(
            tab, wvp.add_storage_cost(
                db.transactions, date, amount, recipient_text
            )
        )
    elif tab == 'tab-bank-charge':
        return vpt.handle_status_message(
            tab, wvp.add_bank_charge(
                db.transactions, date, amount
            )
        )
    elif tab == 'tab-balance':
        return vpt.handle_status_message(
            tab, wvp.add_balance(
                db.balance, amount, month, year
            )
        )

    return vpt.handle_status_message(tab, "Verified!")

@callback(
    Output('dataframe', 'rowData'),
    Input('verify', 'value'),
    State('tabs-access-data', 'value'),
    State('season', 'value'),
    State('membership-type-find', 'value')
)
def get_columns(verified: bool, tab: str, season: list[str], m_type: list[str]):
    if not verified:
        return []

    if tab == 'tab-membership-list':
        return fvp.get_membership_list(
            db.members, db.people, db.transactions, season, m_type
        ).to_dict('records')

if __name__ == '__main__':
    app.run(debug=True)
