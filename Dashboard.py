from datetime import datetime, timedelta

from dash import Dash, html, dcc, callback, Output, Input, State
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import dash_ag_grid as dag

from config import BANK_CHARGE, MEMBER_TYPES, NOT_OK, OK, SEASONS, STORAGE_COST, STORAGE_OWNER, TRANS_TYPES, URI
import add_vpdata as avp
import find_vpdata as fvp
import transaction_vpdata as tvp
import vp_tools as vpt

client = MongoClient(URI, server_api=ServerApi('1'))
db = client.myDatabase
NAMES = [
    {
        'label': f"{x['surname']}, {x['first_name']}",
        'value': str(x['_id']) + '|' + x['first_name'] + ' ' + x['surname'],
    }
    for x in db.people.find({})
]
PRODUCTIONS = vpt.get_productions_list(db.productions, db.festivals)
VERIFICATION = [
    {'label': OK, 'value': True},
    {'label': NOT_OK, 'value': False},
]
transaction_fields = {
    't-transaction-type': {'type': 'dropdown', 'options': TRANS_TYPES},
    't-membership-type': {'type': 'dropdown', 'options': MEMBER_TYPES},
    't-date': {'type': 'date'},
    't-amount': {'type': 'number'},
    't-description': {'type': 'text'},
    't-recipient': {'type': 'dropdown', 'options': NAMES},
    't-recipient-text': {'type': 'text'},
    't-member': {'type': 'dropdown-multi', 'options': NAMES},
    't-member-1': {'type': 'text'},
    't-member-2': {'type': 'text'},
    't-member-3': {'type': 'text'},
    't-production': {'type': 'dropdown', 'options': PRODUCTIONS},
    # 'season': {'type': 'dropdown-multi', 'options': SEASONS},
    # 'membership-type-find': {'type': 'dropdown-multi', 'options': MEMBER_TYPES},
    't-verify': {'type': 'dropdown', 'options': VERIFICATION},
}
transaction_tabs = {
    't-tab-misc': {
        'label': "Add Transaction",
        'defaults': {
            't-transaction-type': None,
            't-date': datetime.today().date(),
            't-amount': None,
            't-description': None,
            't-recipient': None,
            't-recipient-text': None,
            't-production': None,
        },
    },
    't-tab-renew': {
        'label': "Add Renewing Member(s)",
        'defaults': {
            't-membership-type': 'Full',
            't-date': datetime.today().date(),
            't-amount': 95,
            't-member': None,
        },
    },
    't-tab-new': {
        'label': "Add New Member(s)",
        'defaults': {
            't-membership-type': 'Full',
            't-date': datetime.today().date(),
            't-amount': 95,
            't-member-1': None,
            't-member-2': None,
            't-member-3': None,
        },
    },
    't-tab-mixed': {
        'label': "Add Mixed New/Renewing Members",
        'keep': [
            'membership-type', 'date', 'amount',
            'member', 'member-1', 'member-2', 'member-3'
        ],
        'defaults': {
            't-membership-type': 'Full',
            't-date': datetime.today().date(),
            't-amount': None,
            't-member': None,
            't-member-1': None,
            't-member-2': None,
            't-member-3': None,
        },
    },
    't-tab-storage': {
        'label': "Add Storage",
        'defaults': {
            't-transaction-type': 'Storage',
            't-date': datetime.today().date().replace(day=1) - timedelta(1),
            't-amount': STORAGE_COST,
            't-recipient-text': STORAGE_OWNER,
        },
    },
    't-tab-bank-charge': {
        'label': "Add Bank Charge",
        'defaults': {
            't-transaction-type': 'Bank Charges',
            't-date': datetime.today().date().replace(day=1) - timedelta(1),
            't-amount': BANK_CHARGE,
        },
    },
    # 'tab-membership-list': {
    #     'label': "Show Members",
    #     'defaults': {
    #         'season': SEASONS[-1],
    #         'membership-type-find': MEMBER_TYPES,
    #     },
    # },
}

main_tabs = {
    'transactions': 'Insert New Transactions',
    'insert-records': 'Insert New Record',
    # 'update-records': 'Update a Record',
    # 'find-records': 'Find Records',
}

app_layout = [
    html.H1('Village Players Database'),
    dcc.Tabs(
        id='main-tabs', value=list(main_tabs.keys())[0], children=[
            dcc.Tab(label=label, value=value) for value, label in main_tabs.items()
        ]
    )
]

transaction_section = [
    html.H2('Add New Transaction: '),
    dcc.Tabs(
        id='t-tabs', value=list(transaction_tabs.keys())[0], children=[
            dcc.Tab(label=layout['label'], value=tab)
            for tab, layout in transaction_tabs.items()
        ]
    )
]

for field, layout in transaction_fields.items():
    transaction_section.append(
        html.Div([
            field[2:].replace('-', ' ').title() + ": ",
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
transaction_section.append(html.Div(id='t-returned'))

app_layout.append(
    html.Div(
        transaction_section,
        id='section-transactions',
        hidden=False
    )
)

app_layout.append(
    html.Div(
        [
            html.H2('Add New Database Entry: '),
            dcc.Tabs(
                id='a-tabs', value='a-tab-balance', children=[
                    dcc.Tab(label="Add New Balance", value='a-tab-balance')
                ]
            ),
            html.Div(
                [
                    "Amount: ",
                    dcc.Input(id='a-balance-amount', type='number'),
                    "Month: ",
                    dcc.Input(
                        id='a-balance-month', type='number',
                        value=(datetime.today().date().replace(day=1) - timedelta(1)).month
                    ),
                    "Year: ",
                    dcc.Input(
                        id='a-balance-year', type='number',
                        value=(datetime.today().date().replace(day=1) - timedelta(1)).year
                    ),
                ],
                id='a-balance',
                hidden=False
            ),
            html.Div([
                "Verify: ",
                dcc.Dropdown(id='a-verify', options=VERIFICATION, value=False),
            ]),
            html.Div(id='a-returned')
        ],
        id='section-insert-records',
        hidden=True
    )
)


# app_layout.append(
#     html.Div([
#         dag.AgGrid(
#             id='dataframe',
#             rowData=[],
#             columnDefs=[
#                 {'field': 'season'},
#                 {'field': 'type'},
#                 {'field': 'surname'},
#                 {'field': 'first_name', 'headerName': 'First Name'},
#                 {'field': 'email'},
#             ],
#         )
#     ])
# )

app = Dash(__name__)

app.layout = html.Div(app_layout)

def switch_main_tab(section: str):
    @callback(
        Output(f'section-{section}', 'hidden'),
        Input('main-tabs', 'value')
    )
    def show_main_tab(tab: str) -> bool:
        return tab != section

for tab in main_tabs.keys():
    switch_main_tab(tab)

def falsify_on_tab_switch(prefix: str):
    @callback(
        Output(f'{prefix}-verify', 'value'),
        Input(f'{prefix}-tabs', 'value')
    )
    def verify_falsification(tab: str):
        return False

for prefix in ['t', 'a']:
    falsify_on_tab_switch(prefix)

def update_div(field):
    @callback(
        Output(f'div-{field}', 'hidden'),
        Input('t-tabs', 'value')
    )
    def hide_transaction_type(tab: str):
        return not field in transaction_tabs[tab]['defaults'].keys()

    @callback(
        Output(field, 'date' if transaction_fields[field]['type'] == 'date' else 'value'),
        Input('t-tabs', 'value')
    )
    def hide_transaction_type(tab: str):
        return transaction_tabs[tab]['defaults'].get(field)

for field in transaction_fields.keys():
    if field != 't-verify':
        update_div(field)

# @callback(
#     Output('dataframe', 'columnDefs'),
#     Input('tabs-access-data', 'value')
# )
# def reset_columns_on_tab_switch(tab: str):
#     return []

@callback(
    Output('t-returned', 'children'),
    Input('t-verify', 'value'),
    State('t-tabs', 'value'),
    State('t-transaction-type', 'value'),
    State('t-membership-type', 'value'),
    State('t-date', 'date'),
    State('t-amount', 'value'),
    State('t-description', 'value'),
    State('t-recipient', 'value'),
    State('t-recipient-text', 'value'),
    State('t-member', 'value'),
    State('t-member-1', 'value'),
    State('t-member-2', 'value'),
    State('t-member-3', 'value'),
    State('t-production', 'value')
)
def return_status_transaction(
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
    production: str | None
) -> str:
    if not verified:
        try:
            client.admin.command('ping')
            return vpt.handle_status_message(tab, "Ping successful!")
        except Exception as e:
            return vpt.handle_status_message(tab, e)

    if tab == 't-tab-misc':
        return vpt.handle_status_message(
            tab, tvp.add_misc_transaction(
                db.transactions, t_type, date, amount, description, recipient,
                recipient_text, production
            )
        )
    elif tab == 't-tab-renew':
        return vpt.handle_status_message(
            tab, tvp.add_renew_transaction(
                db.transactions, db.members, date, m_type, amount, member
            )
        )
    elif tab == 't-tab-new':
        return vpt.handle_status_message(
            tab, tvp.add_new_transaction(
                db.transacations, db.people, db.members, date, m_type, amount,
                member_1, member_2, member_3
            )
        )
    elif tab == 't-tab-storage':
        return vpt.handle_status_message(
            tab, tvp.add_storage_cost(
                db.transactions, date, amount, recipient_text
            )
        )
    elif tab == 't-tab-bank-charge':
        return vpt.handle_status_message(
            tab, tvp.add_bank_charge(
                db.transactions, date, amount
            )
        )

    return vpt.handle_status_message(tab, "Verified!")

@callback(
    Output('a-returned', 'children'),
    Input('a-verify', 'value'),
    State('a-tabs', 'value'),
    State('a-balance-amount', 'value'),
    State('a-balance-month', 'value'),
    State('a-balance-year', 'value')
)
def return_status_add(
    verified: bool,
    tab: str,
    amount: float | None,
    month: int | None,
    year: int | None
) -> str:
    if not verified:
        try:
            client.admin.command('ping')
            return vpt.handle_status_message(tab, "Ping successful!")
        except Exception as e:
            return vpt.handle_status_message(tab, e)

    if tab == 'a-tab-balance':
        return vpt.handle_status_message(
            tab, avp.add_balance(
                db.balance, amount, month, year
            )
        )

    return vpt.handle_status_message(tab, "Verified!")

# @callback(
#     Output('dataframe', 'rowData'),
#     Input('verify', 'value'),
#     State('tabs-access-data', 'value'),
#     State('season', 'value'),
#     State('membership-type-find', 'value')
# )
# def get_columns(verified: bool, tab: str, season: list[str], m_type: list[str]):
#     if not verified:
#         return []

#     if tab == 'tab-membership-list':
#         return fvp.get_membership_list(
#             db.members, db.people, db.transactions, season, m_type
#         ).to_dict('records')

if __name__ == '__main__':
    app.run(debug=True)
