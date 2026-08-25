from datetime import datetime, timedelta

from bson.decimal128 import Decimal128
from bson.objectid import ObjectId
from dash import Dash, html, dcc, callback, Output, Input, State
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import dash_ag_grid as dag

from config import (
    BANK_CHARGE, GENDERS, MEMBER_TYPES, NOT_OK, OK, ROLE_TYPES, SEASONS,
    STORAGE_COST, STORAGE_OWNER, TRANS_TYPES, URI
)
import add_vpdata as avp
import find_vpdata as fvp
import transaction_vpdata as tvp
import update_vpdata as uvp
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
FESTIVALS = [
    {'label': x['title'], 'value': str(x['_id'])} for x in db.festivals.find({})
]
PRODUCTIONS = vpt.get_productions_list(db.productions, db.festivals)
VERIFICATION = [
    {'label': OK, 'value': True},
    {'label': NOT_OK, 'value': False},
]
transaction_fields = {
    't-transaction-type': {'type': 'dropdown', 'options': [''] + TRANS_TYPES},
    't-membership-type': {'type': 'dropdown', 'options': [''] + MEMBER_TYPES},
    't-date': {'type': 'date'},
    't-amount': {'type': 'number'},
    't-description': {'type': 'text'},
    't-recipient': {'type': 'dropdown', 'options': [''] + NAMES},
    't-recipient-text': {'type': 'text'},
    't-member': {'type': 'dropdown-multi', 'options': NAMES},
    't-member-1': {'type': 'text'},
    't-member-2': {'type': 'text'},
    't-member-3': {'type': 'text'},
    't-production': {'type': 'dropdown', 'options': [''] + PRODUCTIONS},
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
    'insert-records': 'Insert a New Record',
    'update-records': 'Update a Record',
    # 'find-records': 'Find Records',
}

app_layout = [
    html.H1('Village Players Database Interface'),
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

non_transaction_tabs = {
    'a': ['balance', 'festival', 'production', 'cast-crew', 'committee', 'person'],
    'u': ['balance', 'festival', 'production', 'cast-crew', 'committee', 'person'],
}
update_fields = {
    'balance': {'collection': db.balance, 'value': {'amount': 'balance'}, 'date': []},
    'festival': {
        'collection': db.festivals, 'value': {'venue': 'venue'},
        'date': {'open': 'open_date', 'close': 'close_date'}
    },
    'production': {
        'collection': db.productions,'value': {'venue': 'venue', 'festival': 'festival'},
        'date': {'open': 'open_date', 'close': 'close_date'}
    },
    'cast-crew': {'collection': db.castcrew, 'value': {'role-name': 'role_name'}, 'date': []},
    'committee': {'collection': db.committee,'value': {}, 'date': {}},
    'person': {
        'collection': db.people,
        'value': {
            'address': 'address', 'postcode': 'postcode', 'address-private': 'address_private',
            'home-phone': 'home_phone', 'home-phone-private': 'home_phone_private',
            'mobile': 'mobile', 'mobile-private': 'mobile_private', 'email': 'email',
            'email-private': 'email_private', 'gender': 'gender'
        },
        'date': {'gdpr': 'gdpr'},
    }
}

app_layout.append(
    html.Div(
        [
            html.H2('Add New Database Entry: '),
            dcc.Tabs(
                id='a-tabs', value='a-tab-balance', children=[
                    dcc.Tab(label="Add New Balance", value='a-tab-balance'),
                    dcc.Tab(label="Add New Festival", value='a-tab-festival'),
                    dcc.Tab(label="Add New Production", value='a-tab-production'),
                    dcc.Tab(label="Add New Cast or Crew Member", value='a-tab-cast-crew'),
                    dcc.Tab(label="Add New Committee Member", value='a-tab-committee'),
                    dcc.Tab(label="Add New Person", value='a-tab-person'),
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
            html.Div(
                [
                    "Name: ",
                    dcc.Input(id='a-festival-name', type='text'),
                    "Venue: ",
                    dcc.Input(id='a-festival-venue', type='text'),
                    "Open Date: ",
                    dcc.DatePickerSingle(id='a-festival-open'),
                    "Close Date: ",
                    dcc.DatePickerSingle(id='a-festival-close'),
                ],
                id='a-festival',
                hidden=True
            ),
            html.Div(
                [
                    "Name: ",
                    dcc.Input(id='a-production-name', type='text'),
                    "Venue: ",
                    dcc.Input(id='a-production-venue', type='text'),
                    "Open Date: ",
                    dcc.DatePickerSingle(id='a-production-open'),
                    "Close Date: ",
                    dcc.DatePickerSingle(id='a-production-close'),
                    "Festival: ",
                    dcc.Dropdown(id='a-production-festival', options=[''] + FESTIVALS),
                ],
                id='a-production',
                hidden=True
            ),
            html.Div(
                [
                    "Person: ",
                    dcc.Dropdown(id='a-cast-crew-person', options=NAMES),
                    "Production: ",
                    dcc.Dropdown(id='a-cast-crew-production', options=PRODUCTIONS),
                    "Role: ",
                    dcc.Dropdown(
                        id='a-cast-crew-role',
                        options=[''] + [{'label': x, 'value': x.lower()} for x in ROLE_TYPES]
                    ),
                    "Role Name: ",
                    dcc.Input(id='a-cast-crew-role-name', type='text'),
                ],
                id='a-cast-crew',
                hidden=True
            ),
            html.Div(
                [
                    "Person: ",
                    dcc.Dropdown(id='a-committee-person', options=NAMES),
                    "Season: ",
                    dcc.Dropdown(id='a-committee-season', options=SEASONS),
                    "Position: ",
                    dcc.Input(id='a-committee-position', type='text'),
                ],
                id='a-committee',
                hidden=True
            ),
            html.Div(
                [
                    "First Name: ",
                    dcc.Input(id='a-person-first-name', type='text'),
                    "Surname: ",
                    dcc.Input(id='a-person-surname', type='text'),
                    "Address (first line): ",
                    dcc.Input(id='a-person-address', type='text'),
                    "Postcode (including town): ",
                    dcc.Input(id='a-person-postcode', type='text'),
                    "Address is Private: ",
                    dcc.Dropdown(id='a-person-address-private', options=[True, False], value=True),
                    "Home Phone: ",
                    dcc.Input(id='a-person-home-phone', type='text'),
                    "Home Phone is Private: ",
                    dcc.Dropdown(id='a-person-home-phone-private', options=[True, False], value=True),
                    "Mobile: ",
                    dcc.Input(id='a-person-mobile', type='text'),
                    "Mobile is Private: ",
                    dcc.Dropdown(id='a-person-mobile-private', options=[True, False], value=True),
                    "Email: ",
                    dcc.Input(id='a-person-email', type='text'),
                    "Email is Private: ",
                    dcc.Dropdown(id='a-person-email-private', options=[True, False], value=True),
                    "Gender: ",
                    dcc.Dropdown(
                        id='a-person-gender',
                        options=[''] + [{'label': x, 'value': x.lower()} for x in GENDERS]
                    ),
                    "GDPR Signed On: ",
                    dcc.DatePickerSingle(id='a-person-gdpr'),
                ],
                id='a-person',
                hidden=True
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

app_layout.append(
    html.Div(
        [
            html.H2('Update Database Entry: '),
            dcc.Tabs(
                id='u-tabs', value='u-tab-balance', children=[
                    dcc.Tab(label="Update Balance", value='u-tab-balance'),
                    dcc.Tab(label="Update Festival", value='u-tab-festival'),
                    dcc.Tab(label="Update Production", value='u-tab-production'),
                    dcc.Tab(label="Update Cast or Crew Member", value='u-tab-cast-crew'),
                    dcc.Tab(label="Update Committee Member", value='u-tab-committee'),
                    dcc.Tab(label="Update Person", value='u-tab-person'),
                    # dcc.Tab(label="Update Transaction", value='u-tab-transaction'),
                    # dcc.Tab(label="Update Member", value='u-tab-member'),
                ]
            ),
            html.Div(
                [
                    "Select Entry: ",
                    dcc.Dropdown(id='u-balance-select', options=[
                        {
                            'label': entry['date'].strftime("%B %Y"),
                            'value': str(entry['_id']),
                        }
                        for entry in db.balance.find({})
                    ]),
                    "Amount: ",
                    dcc.Input(id='u-balance-amount', type='number'),
                ],
                id='u-balance',
                hidden=False
            ),
            html.Div(
                [
                    "Select Entry: ",
                    dcc.Dropdown(id='u-festival-select', options=[
                        {
                            'label': entry['title'],
                            'value': str(entry['_id']),
                        }
                        for entry in db.festivals.find({})
                    ]),
                    "Venue: ",
                    dcc.Input(id='u-festival-venue', type='text'),
                    "Open Date: ",
                    dcc.DatePickerSingle(id='u-festival-open'),
                    "Close Date: ",
                    dcc.DatePickerSingle(id='u-festival-close'),
                ],
                id='u-festival',
                hidden=True
            ),
            html.Div(
                [
                    "Select Entry: ",
                    dcc.Dropdown(id='u-production-select', options=[
                        {
                            'label': entry['title'],
                            'value': str(entry['_id']),
                        }
                        for entry in db.productions.find({})
                    ]),
                    "Venue: ",
                    dcc.Input(id='u-production-venue', type='text'),
                    "Open Date: ",
                    dcc.DatePickerSingle(id='u-production-open'),
                    "Close Date: ",
                    dcc.DatePickerSingle(id='u-production-close'),
                    "Festival: ",
                    dcc.Dropdown(id='u-production-festival', options=[''] + FESTIVALS),
                ],
                id='u-production',
                hidden=True
            ),
            html.Div(
                [
                    "Select Entry: ",
                    dcc.Dropdown(id='u-cast-crew-select', options=[
                        {
                            'label': f"{db.productions.find_one({'_id': entry['production']})['title']}"
                                f" / {db.people.find_one({'_id': entry['person']})['surname']}"
                                f" / {entry['role']}",
                            'value': str(entry['_id']),
                        }
                        for entry in db.castcrew.find({})
                    ]),
                    "Role Name: ",
                    dcc.Input(id='u-cast-crew-role-name', type='text'),
                ],
                id='u-cast-crew',
                hidden=True
            ),
            html.Div(
                [
                    "Select Entry: ",
                    dcc.Dropdown(id='u-committee-select', options=[
                        {
                            'label': f"{entry['season']} / {entry['position']}"
                                f" / {db.people.find_one({'_id': entry['holder']})['surname']}",
                            'value': str(entry['_id']),
                        }
                        for entry in db.committee.find({})
                    ]),
                ],
                id='u-committee',
                hidden=True
            ),
            html.Div(
                [
                    "Select Entry: ",
                    dcc.Dropdown(id='u-person-select', options=[
                        {
                            'label': f"{entry['first_name']} {entry['surname']}",
                            'value': str(entry['_id']),
                        } for entry in db.people.find({})
                    ]),
                    "Address (first line): ",
                    dcc.Input(id='u-person-address', type='text'),
                    "Postcode (including town): ",
                    dcc.Input(id='u-person-postcode', type='text'),
                    "Address is Private: ",
                    dcc.Dropdown(id='u-person-address-private', options=[True, False], value=True),
                    "Home Phone: ",
                    dcc.Input(id='u-person-home-phone', type='text'),
                    "Home Phone is Private: ",
                    dcc.Dropdown(id='u-person-home-phone-private', options=[True, False], value=True),
                    "Mobile: ",
                    dcc.Input(id='u-person-mobile', type='text'),
                    "Mobile is Private: ",
                    dcc.Dropdown(id='u-person-mobile-private', options=[True, False], value=True),
                    "Email: ",
                    dcc.Input(id='u-person-email', type='text'),
                    "Email is Private: ",
                    dcc.Dropdown(id='u-person-email-private', options=[True, False], value=True),
                    "Gender: ",
                    dcc.Dropdown(
                        id='u-person-gender',
                        options=[''] + [{'label': x, 'value': x.lower()} for x in GENDERS]
                    ),
                    "GDPR Signed On: ",
                    dcc.DatePickerSingle(id='u-person-gdpr'),
                ],
                id='u-person',
                hidden=True
            ),
            html.Div([
                "Update: ",
                dcc.Dropdown(id='u-update', options=VERIFICATION, value=False)
            ]),
            html.Div([
                "Delete: ",
                dcc.Dropdown(id='u-delete', options=VERIFICATION, value=False)
            ]),
            html.Div(id='u-updated'),
            html.Div(id='u-deleted', hidden=True)
        ],
        id='section-update-records',
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

def unverify_on_tab_switch(prefix: str):
    @callback(
        Output(f'{prefix}-verify', 'value'),
        Input(f'{prefix}-tabs', 'value')
    )
    def verify_falsification(tab: str):
        return False

for prefix in ['t', 'a']:
    unverify_on_tab_switch(prefix)

@callback(
    Output('u-update', 'value'),
    Input('u-tabs', 'value')
)
def update_falsification(tab: str):
    return False

@callback(
    Output('u-delete', 'value'),
    Input('u-tabs', 'value')
)
def delete_falsification(tab: str):
    return False

def update_transaction_div(field):
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
        update_transaction_div(field)

def update_tab_in_other_sections(prefix: str, tab: str):
    @callback(
        Output(f'{prefix}-{tab}', 'hidden'),
        Input(f'{prefix}-tabs', 'value')
    )
    def hide_tab(section_tab: str):
        section_tab = section_tab[2:].replace('tab-', '')
        return tab != section_tab

for prefix, tabs in non_transaction_tabs.items():
    for tab in tabs:
        update_tab_in_other_sections(prefix, tab)

def fill_in_value_update_fields(tab: str, field: str):
    @callback(
        Output(f'u-{tab}-{field}', 'value'),
        Input(f'u-{tab}-select', 'value'),
    )
    def current_value(entry_id: str):
        if not entry_id:
            return
        entry = update_fields[tab]['collection'].find_one({'_id': ObjectId(entry_id)})

        value = entry.get(update_fields[tab]['value'][field])
        if value is None:
            return

        if type(value) == Decimal128:
            value = float(str(value))
        elif type(value) == ObjectId:
            value = str(value)

        return value

def fill_in_date_update_fields(tab: str, field: str):
    @callback(
        Output(f'u-{tab}-{field}', 'date'),
        Input(f'u-{tab}-select', 'value'),
    )
    def current_value(entry_id: str):
        if not entry_id:
            return
        entry = update_fields[tab]['collection'].find_one({'_id': ObjectId(entry_id)})
        return entry.get(update_fields[tab]['date'][field])

for tab in update_fields.keys():
    for field in update_fields[tab]['value']:
        fill_in_value_update_fields(tab, field)

    for field in update_fields[tab]['date']:
        fill_in_date_update_fields(tab, field)


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
    State('a-balance-year', 'value'),
    State('a-festival-name', 'value'),
    State('a-festival-venue', 'value'),
    State('a-festival-open', 'date'),
    State('a-festival-close', 'date'),
    State('a-production-name', 'value'),
    State('a-production-venue', 'value'),
    State('a-production-open', 'date'),
    State('a-production-close', 'date'),
    State('a-production-festival', 'value'),
    State('a-cast-crew-person', 'value'),
    State('a-cast-crew-production', 'value'),
    State('a-cast-crew-role', 'value'),
    State('a-cast-crew-role-name', 'value'),
    State('a-committee-person', 'value'),
    State('a-committee-season', 'value'),
    State('a-committee-position', 'value'),
    State('a-person-first-name', 'value'),
    State('a-person-surname', 'value'),
    State('a-person-address', 'value'),
    State('a-person-postcode', 'value'),
    State('a-person-address-private', 'value'),
    State('a-person-home-phone', 'value'),
    State('a-person-home-phone-private', 'value'),
    State('a-person-mobile', 'value'),
    State('a-person-mobile-private', 'value'),
    State('a-person-email', 'value'),
    State('a-person-email-private', 'value'),
    State('a-person-gender', 'value'),
    State('a-person-gdpr', 'date')
)
def return_status_add(
    verified: bool,
    tab: str,
    balance_amount: float | None,
    balance_month: int | None,
    balance_year: int | None,
    festival_name: str | None,
    festival_venue: str | None,
    festival_open: str | None,
    festival_close: str | None,
    production_name: str | None,
    production_venue: str | None,
    production_open: str | None,
    production_close: str | None,
    production_festival: str | None,
    cast_person: str | None,
    cast_production: str | None,
    cast_role: str | None,
    cast_name: str | None,
    committee_person: str | None,
    committee_season: str | None,
    committee_position: str | None,
    person_first_name: str | None,
    person_surname: str | None,
    person_address: str | None,
    person_postcode: str | None,
    person_address_private: bool | None,
    person_phone: str | None,
    person_phone_private: bool | None,
    person_mobile: str | None,
    person_mobile_private: bool | None,
    person_email: str | None,
    person_email_private: bool | None,
    person_gender: str | None,
    person_gdpr: str | None
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
                db.balance, balance_amount, balance_month, balance_year
            )
        )
    elif tab == 'a-tab-festival':
        return vpt.handle_status_message(
            tab, avp.add_festival(
                db.festivals, festival_name, festival_venue, festival_open, festival_close
            )
        )
    elif tab == 'a-tab-production':
        return vpt.handle_status_message(
            tab, avp.add_production(
                db.productions, production_name, production_venue, production_open,
                production_close, production_festival
            )
        )
    elif tab == 'a-tab-cast-crew':
        return vpt.handle_status_message(
            tab, avp.add_cast_crew(
                db.castcrew, cast_person.split('|')[0], cast_production, cast_role, cast_name
            )
        )
    elif tab == 'a-tab-committee':
        return vpt.handle_status_message(
            tab, avp.add_committee(
                db.committee, committee_person.split('|')[0], committee_season, committee_position
            )
        )
    elif tab == 'a-tab-person':
        return vpt.handle_status_message(
            tab, avp.add_person(
                db.people, person_first_name, person_surname, person_address, person_postcode,
                person_address_private, person_phone, person_phone_private,
                person_mobile, person_mobile_private, person_email, person_email_private,
                person_gender, person_gdpr
            )
        )

    return vpt.handle_status_message(tab, "Verified!")

@callback(
    Output('u-updated', 'children'),
    Input('u-update', 'value'),
    State('u-tabs', 'value'),
    State('u-balance-select', 'value'),
    State('u-balance-amount', 'value'),
    State('u-festival-select', 'value'),
    State('u-festival-venue', 'value'),
    State('u-festival-open', 'date'),
    State('u-festival-close', 'date'),
    State('u-production-select', 'value'),
    State('u-production-venue', 'value'),
    State('u-production-open', 'date'),
    State('u-production-close', 'date'),
    State('u-production-festival', 'value'),
    State('u-cast-crew-select', 'value'),
    State('u-cast-crew-role-name', 'value'),
    State('u-person-select', 'value'),
    State('u-person-address', 'value'),
    State('u-person-postcode', 'value'),
    State('u-person-address-private', 'value'),
    State('u-person-home-phone', 'value'),
    State('u-person-home-phone-private', 'value'),
    State('u-person-mobile', 'value'),
    State('u-person-mobile-private', 'value'),
    State('u-person-email', 'value'),
    State('u-person-email-private', 'value'),
    State('u-person-gender', 'value'),
    State('u-person-gdpr', 'date')
)
def return_status_update(
    verified: bool,
    tab: str,
    balance_id: str | None,
    balance_amount: float | None,
    festival_id: str | None,
    festival_venue: str | None,
    festival_open: str | None,
    festival_close: str | None,
    production_id: str | None,
    production_venue: str | None,
    production_open: str | None,
    production_close: str | None,
    production_festival: str | None,
    cast_id: str | None,
    cast_name: str | None,
    person_id: str | None,
    person_address: str | None,
    person_postcode: str | None,
    person_address_private: bool | None,
    person_phone: str | None,
    person_phone_private: bool | None,
    person_mobile: str | None,
    person_mobile_private: bool | None,
    person_email: str | None,
    person_email_private: bool | None,
    person_gender: str | None,
    person_gdpr: str | None
) -> str:
    if not verified:
        try:
            client.admin.command('ping')
            return vpt.handle_status_message(tab, "Ping successful!")
        except Exception as e:
            return vpt.handle_status_message(tab, e)

    if tab == 'u-tab-balance':
        return vpt.handle_status_message(
            tab, uvp.update_balance(
                db.balance, balance_id, balance_amount
            )
        )
    elif tab == 'u-tab-festival':
        return vpt.handle_status_message(
            tab, uvp.update_festival(
                db.festivals, festival_id, festival_venue, festival_open, festival_close
            )
        )
    elif tab == 'u-tab-production':
        return vpt.handle_status_message(
            tab, uvp.update_production(
                db.productions, production_id, production_venue, production_open,
                production_close, production_festival
            )
        )
    elif tab == 'u-tab-cast-crew':
        return vpt.handle_status_message(
            tab, uvp.update_cast_crew(
                db.castcrew, cast_id, cast_name
            )
        )
    elif tab == 'u-tab-person':
        return vpt.handle_status_message(
            tab, uvp.update_person(
                db.people, person_id, person_address, person_postcode,
                person_address_private, person_phone, person_phone_private,
                person_mobile, person_mobile_private, person_email, person_email_private,
                person_gender, person_gdpr
            )
        )

    return vpt.handle_status_message(tab, "Verified!")

@callback(
    Output('u-deleted', 'hidden'),
    Input('u-delete', 'value')
)
def hide_delete_status(
    verified: bool
) -> bool:
    return not verified

@callback(
    Output('u-deleted', 'children'),
    Input('u-delete', 'value'),
    State('u-tabs', 'value'),
    State('u-balance-select', 'value'),
    State('u-festival-select', 'value'),
    State('u-production-select', 'value'),
    State('u-cast-crew-select', 'value'),
    State('u-committee-select', 'value'),
    State('u-person-select', 'value')
)
def return_status_delete(
    verified: bool,
    tab: str,
    balance_id: str | None,
    festival_id: str | None,
    production_id: str | None,
    cast_id: str | None,
    committee_id: str | None,
    person_id: str | None
) -> str:
    if not verified:
        try:
            client.admin.command('ping')
            return vpt.handle_status_message(tab, "Ping successful!")
        except Exception as e:
            return vpt.handle_status_message(tab, e)

    if tab == 'u-tab-balance':
        return vpt.handle_status_message(
            tab, uvp.delete_record(db.balance, balance_id)
        )
    elif tab == 'u-tab-festival':
        return vpt.handle_status_message(
            tab, uvp.delete_record(db.festivals, festival_id)
        )
    elif tab == 'u-tab-production':
        return vpt.handle_status_message(
            tab, uvp.delete_record(db.productions, production_id)
        )
    elif tab == 'u-tab-cast-crew':
        return vpt.handle_status_message(
            tab, uvp.delete_record(db.castcrew, cast_id)
        )
    elif tab == 'u-tab-committee':
        return vpt.handle_status_message(
            tab, uvp.delete_record(db.committee, committee_id)
        )
    elif tab == 'u-tab-person':
        return vpt.handle_status_message(
            tab, uvp.delete_record(db.people, person_id)
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
