from datetime import datetime, timedelta
import pandas as pd

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
}

main_tabs = {
    'transactions': 'Insert New Transactions',
    'insert-records': 'Insert a New Record',
    'update-records': 'Update a Record',
    'find-records': 'Find Records',
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
    'f': ['member', 'committee', 'balance'],
}

update_fields = {
    'balance': {
        'collection': db.balance, 'value': {'amount': 'balance'}, 'date': [],
        'entry_lambda': lambda x: x['date'].strftime("%B %Y")
    },
    'festival': {
        'collection': db.festivals, 'value': {'venue': 'venue'},
        'date': {'open': 'open_date', 'close': 'close_date'},
        'entry_lambda': lambda x: x['title']
    },
    'production': {
        'collection': db.productions,
        'value': {'venue': 'venue', 'author': 'author', 'festival': 'festival'},
        'date': {'open': 'open_date', 'close': 'close_date'},
        'entry_lambda': lambda x: x['title']
    },
    'cast-crew': {
        'collection': db.castcrew, 'value': {'role-name': 'role_name'}, 'date': [],
        'entry_lambda': lambda x: f"{db.productions.find_one({'_id': x['production']})['title']}"
                                f" / {db.people.find_one({'_id': x['person']})['surname']}"
                                f" / {x['role']}"
    },
    'committee': {
        'collection': db.committee, 'value': {}, 'date': {},
        'entry_lambda': lambda x: f"{x['season']} / {x['position']}"
                                f" / {db.people.find_one({'_id': x['holder']})['surname']}"
    },
    'person': {
        'collection': db.people,
        'value': {
            'address': 'address', 'postcode': 'postcode', 'address-private': 'address_private',
            'home-phone': 'home_phone', 'home-phone-private': 'home_phone_private',
            'mobile': 'mobile', 'mobile-private': 'mobile_private', 'email': 'email',
            'email-private': 'email_private', 'gender': 'gender',
            'committee-email': 'committee_email'
        },
        'date': {'gdpr': 'gdpr'},
        'entry_lambda': lambda x: f"{x['first_name']} {x['surname']}"
    }
}

# Add
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
                    "Author: ",
                    dcc.Input(id='a-production-author', type='text'),
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
                    dcc.Dropdown(id='a-cast-crew-role', options=[''] + ROLE_TYPES),
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
                    dcc.Dropdown( id='a-person-gender', options=[''] + GENDERS),
                    "GDPR Signed On: ",
                    dcc.DatePickerSingle(id='a-person-gdpr'),
                    "Committee Email: ",
                    dcc.Input(id='a-person-committee-email', type='text'),
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

# Update
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
                    "Author: ",
                    dcc.Input(id='u-production-author', type='text'),
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
                    dcc.Dropdown(id='u-person-gender', options=[''] + GENDERS),
                    "GDPR Signed On: ",
                    dcc.DatePickerSingle(id='u-person-gdpr'),
                    "Committee Email: ",
                    dcc.Input(id='u-person-committee-email', type='text'),
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

# Find
app_layout.append(
    html.Div(
        [
            html.H2('Find Records: '),
            dcc.Tabs(
                id='f-tabs', value='f-tab-member', children=[
                    dcc.Tab(label="Members", value='f-tab-member'),
                    dcc.Tab(label="Committee", value='f-tab-committee'),
                    dcc.Tab(label="Balances", value='f-tab-balance'),
                ]
            ),
            html.Div(
                [
                    "Select Seasons: ",
                    dcc.Dropdown(id='f-member-seasons', multi=True, options=SEASONS, value=[SEASONS[0]]),
                    "Select Membership Types: ",
                    dcc.Dropdown(
                        id='f-member-types', multi=True, options=MEMBER_TYPES, value=MEMBER_TYPES
                    ),
                    "Select People: ",
                    dcc.Dropdown(id='f-member-persons', multi=True, options=NAMES),
                    "Select Columns: ",
                    dcc.Dropdown(
                        id='f-member-columns', multi=True, options=[
                            'Season', 'Membership Type', 'Carry Over', 'First Name',
                            'Surname', 'Address', 'Postcode', 'Address Private',
                            'Home Phone', 'Home Phone Private', 'Mobile', 'Mobile Private',
                            'Email', 'Email Private', 'Gender', 'GDPR', 'Payment Amount',
                            'Payment Date',
                        ],
                        value=['Season', 'Membership Type', 'First Name', 'Surname', 'Email']
                    ),
                    dag.AgGrid(
                        id='f-member-list',
                        columnDefs=[
                            {'field': 'season'},
                            {'field': 'membership_type', 'headerName': 'Membership Type'}, 
                            {'field': 'first_name', 'headerName': 'First Name'}, 
                            {'field': 'surname'}, 
                            {'field': 'email'}, 
                        ]
                    )
                ],
                id='f-member',
                hidden=False
            ),
            html.Div(
                [
                    "Select Seasons: ",
                    dcc.Dropdown(id='f-committee-seasons', options=SEASONS, multi=True, value=[SEASONS[0]]),
                    dag.AgGrid(
                        id='f-committee-list',
                        columnDefs=[
                            {'field': 'season'},
                            {'field': 'position'}, 
                            {'field': 'first_name', 'headerName': 'First Name'}, 
                            {'field': 'surname'}, 
                            {'field': 'committee_email', 'headerName': 'Email'}, 
                        ]
                    )
                ],
                id='f-committee',
                hidden=True
            ),
            html.Div(
                [
                    "Select Seasons: ",
                    dcc.Dropdown(id='f-balance-seasons', options=SEASONS, multi=True, value=[SEASONS[0]]),
                    dag.AgGrid(
                        id='f-balance-history',
                        columnDefs=[{'field': 'month'}, {'field': 'balance'}]
                    )
                ],
                id='f-balance',
                hidden=True
            ),
        ],
        id='section-find-records',
        hidden=True
    )
)

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

def update_dropdown_menus(tab: str):
    @callback(
        Output(f'u-{tab}-select', 'options'),
        Input('a-returned', 'children'),
        Input('u-updated', 'children'),
        Input('u-deleted', 'children')
    )
    def update_dropdown_menu(add: str, update: str, delete: str):
        return [
            {
                'label': update_fields[tab]['entry_lambda'](entry),
                'value': str(entry['_id']),
            }
            for entry in update_fields[tab]['collection'].find({})
        ]

for tab in update_fields.keys():
    update_dropdown_menus(tab)

@callback(
    Output('f-member-list', 'rowData'),
    Input('f-member-seasons', 'value'),
    Input('f-member-types', 'value'),
    Input('f-member-persons', 'value')
)
def load_member_list(seasons: list[str], types: list[str], names: list[str]):
    if not seasons or not types or not names:
        return pd.DataFrame().to_dict('records')

    members_filter = {'season': {'$in': seasons}, 'type': {'$in': types}}
    people_filter = {}
    if names:
        persons = [ObjectId(name.split('|')[0]) for name in names]
        members_filter['person'] = {'$in': persons}
        people_filter['_id'] = {'$in': persons}

    members = pd.DataFrame(db.members.find(members_filter))
    if members.shape[0] == 0:
        return pd.DataFrame().to_dict('records')

    members.set_index('_id', inplace=True)
    people = pd.DataFrame(db.people.find(people_filter)).set_index('_id')
    transactions = pd.DataFrame(
        db.transactions.find({'Type': 'Membership Subscription', 'Amount': {'$gt': 0}})
    ).set_index('_id')[['Date', 'Amount']]

    members = members.join(people, 'person').join(transactions, 'payment')
    members = members[[
        'season', 'type', 'carry_over', 'first_name', 'surname', 'address', 'postcode',
        'address_private', 'home_phone', 'home_phone_private', 'mobile', 'mobile_private',
        'email', 'email_private', 'gender', 'gdpr', 'Amount', 'Date'
    ]]
    members.columns = [
        'season', 'membership_type', 'carry_over', 'first_name', 'surname', 'address', 'postcode',
        'address_private', 'home_phone', 'home_phone_private', 'mobile', 'mobile_private',
        'email', 'email_private', 'gender', 'gdpr', 'payment_amount', 'payment_date'
    ]
    members.gdpr = members.gdpr.astype(str)
    members.payment_amount = members.payment_amount.astype(str)
    members.payment_date = members.payment_date.astype(str)
    members.sort_values(['season', 'surname'], inplace=True)
    return members.to_dict('records')

@callback(
    Output('f-member-list', 'columnDefs'),
    Input('f-member-columns', 'value')
)
def change_member_list_columns(columns: list[str]):
    return [
        {'field': column.replace(' ', '_').lower(), 'headerName': column}
        for column in columns
    ]

@callback(
    Output('f-committee-list', 'rowData'),
    Input('f-committee-seasons', 'value')
)
def load_committee_list(seasons: list[str]):
    if not seasons:
        return pd.DataFrame().to_dict('records')

    committee = pd.DataFrame(db.committee.find({'season': {'$in': seasons}}))
    if committee.shape[0] == 0:
        return pd.DataFrame().to_dict('records')

    committee.set_index('_id', inplace=True)
    people = pd.DataFrame(db.people.find({})).set_index('_id')
    committee = committee.join(people, 'holder')
    committee.drop(['gdpr', 'holder'], inplace=True, axis=1)
    committee.position = committee.position.apply(lambda x: x.title())
    committee.sort_values('season', inplace=True)
    return committee.to_dict('records')

@callback(
    Output('f-balance-history', 'rowData'),
    Input('f-balance-seasons', 'value')
)
def load_balance_history(seasons: list[str]):
    if not seasons:
        return pd.DataFrame().to_dict('records')

    years = [datetime(int(season[:4]), 5, 25) for season in seasons]

    balances = pd.DataFrame(db.balance.find({}))
    datasets = [
        balances.loc[balances.date.apply(lambda x: x > year and x < year + timedelta(375))]
        for year in years
    ]
    dataset = pd.concat(datasets)
    dataset.balance = dataset.balance.astype(str)
    dataset.drop_duplicates(inplace=True)
    dataset.sort_values('date', ascending=False, inplace=True)
    dataset['month'] = dataset.date.apply(lambda x: x.strftime('%d %B %Y'))
    return dataset[['month', 'balance']].to_dict('records')

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
    State('a-production-author', 'value'),
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
    State('a-person-gdpr', 'date'),
    State('a-person-committee-email', 'value')
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
    production_author: str | None,
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
    person_gdpr: str | None,
    person_committee_email: str | None
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
                db.productions, production_name, production_venue, production_author,
                production_open, production_close, production_festival
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
                person_gender, person_gdpr, person_committee_email
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
    State('u-production-author', 'value'),
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
    State('u-person-gdpr', 'date'),
    State('u-person-committee-email', 'value')
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
    production_author: str | None,
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
    person_gdpr: str | None,
    person_committee_email: str | None
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
                db.productions, production_id, production_venue, production_author,
                production_open, production_close, production_festival
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
                person_gender, person_gdpr, person_committee_email
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
            tab, uvp.delete_record(
                db.festivals, festival_id,
                {db.productions: 'festival', db.transactions: 'Production'}
            )
        )
    elif tab == 'u-tab-production':
        return vpt.handle_status_message(
            tab, uvp.delete_record(
                db.productions, production_id,
                {db.castcrew: 'production', db.transactions: 'Production'}
            )
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
            tab, uvp.delete_record(
                db.people, person_id,
                {
                    db.castcrew: 'person',
                    db.committee: 'holder',
                    db.members: 'person',
                    db.transactions: 'Recipient',
                }
            )
        )

    return vpt.handle_status_message(tab, "Verified!")

if __name__ == '__main__':
    app.run(debug=True)
