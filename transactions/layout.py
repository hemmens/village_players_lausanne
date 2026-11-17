from dash import html, dcc
import dash_ag_grid as dag

from variables import MEMBER_TYPES, SEASONS, TRANSACTION_TYPES

transactions_lookup_layout = [
    dcc.Store(id='f-transactions-loaded', data=True),
    dcc.Store(id='f-transactions-role', storage_type='session'),
    html.H1('Village Players Database Interface'),
    html.H2('Transactions'),
    html.Div(
        "Committee access only", id='f-transactions-no-access', hidden=False
    ),
    html.Div(
        [
            dcc.Download(id='f-transactions-download'),
            html.Label("Transaction Type: "),
            dcc.Dropdown(id='f-transactions-type', multi=True, options=TRANSACTION_TYPES),
            html.Label("Start Date: "),
            dcc.DatePickerSingle(id='f-transactions-start-date', clearable=True),
            html.Label("End Date: "),
            dcc.DatePickerSingle(id='f-transactions-end-date', clearable=True),
            html.Label("Recipient: "),
            dcc.Dropdown(id='f-transactions-recipient', multi=True, options=[]),
            html.Label("Production: "),
            dcc.Dropdown(id='f-transactions-production', multi=True, options=[]),
            dag.AgGrid(
                id='f-transactions-list',
                columnDefs=[
                    {'field': 'Type', 'width': 200},
                    {'field': 'Reference', 'width': 100},
                    {'field': 'Date', 'width': 200},
                    {'field': 'Amount', 'width': 100},
                    {'field': 'Description', 'width': 300},
                    {'field': 'Recipient', 'width': 300},
                    {'field': 'Production', 'width': 300},
                ]
            ),
            html.Button("Export to Excel", id='f-transactions-button'),
        ],
        id='f-transactions-access',
        hidden=True
    ),
    html.Div(
        [
            html.A(
                html.Button("Insert", id='f-transactions-insert'), href='/transactions/insert/'
            ),
            # html.A(
            #     html.Button("Update", id='f-transactions-update'), href='/transactions/update/'
            # ),
        ],
        id='f-transactions-treasurer-access',
        hidden=True
    ),
    html.A(
        html.Button("Home", id='f-transactions-home'), href='/'
    ),
]

transactions_insert_layout = [
    dcc.Store(id='a-transactions-loaded', data=True),
    dcc.Store(id='a-transactions-role', storage_type='session'),
    html.H1('Village Players Database Interface'),
    html.H2('Transactions - Insert'),
    html.Div(
        "Treasurer access only", id='a-transactions-no-access', hidden=False
    ),
    html.Div(
        [
            html.Label("Transaction Type: "),
            dcc.Dropdown(id='a-transactions-type', options=TRANSACTION_TYPES),
            html.Label("Date: "),
            dcc.DatePickerSingle(id='a-transactions-date'),
            html.Label("Amount: "),
            dcc.Input(id='a-transactions-amount', type='number'),
            html.Label("Description: "),
            dcc.Input(id='a-transactions-description', type='text'),
            html.Label("Recipient: "),
            dcc.Dropdown(id='a-transactions-recipient', options=[]),
            html.Label("Recipient Text: "),
            dcc.Input(id='a-transactions-recipient-text', type='text'),
            html.Label("Membership Type: "),
            dcc.Dropdown(id='a-transactions-member-type', options=[''] + MEMBER_TYPES),
            html.Label("Season: "),
            dcc.Dropdown(id='a-transactions-season', options=[''] + SEASONS),
            html.Label("Renewing Member(s): "),
            dcc.Dropdown(id='a-transactions-renew', multi=True, options=[]),
            html.Label("New Member 1 (use format 'Surname, First Name(s)'): "),
            dcc.Input(id='a-transactions-new-1', type='text'),
            html.Label("New Member 2 (format see above): "),
            dcc.Input(id='a-transactions-new-2', type='text'),
            html.Label("New Member 3 (format see above): "),
            dcc.Input(id='a-transactions-new-3', type='text'),
            html.Label("Existing Member: "),
            dcc.Dropdown(id='a-transactions-existing', options=[]),
            html.Label("Production: "),
            dcc.Dropdown(id='a-transactions-production', options=[]),
            html.Div(id='a-transactions-message'),
            html.Button("Insert New Transaction", id='a-transactions-insert'),
            html.A(
                html.Button("Lookup", id='f-transactions-lookup'), href='/transactions/lookup/'
            ),
            # html.A(
            #     html.Button("Update", id='a-transactions-update'), href='/transactions/update/'
            # ),
        ],
        id='a-transactions-access',
        hidden=True
    ),
    html.A(
        html.Button("Home", id='a-transactions-home'), href='/'
    ),
]
