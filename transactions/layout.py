from dash import html, dcc

from variables import MEMBER_TYPES, SEASONS, TRANSACTION_TYPES

transactions_insert_layout = [
    dcc.Store(id='a-transactions-loaded', data=True),
    dcc.Store(id='a-transactions-role', storage_type='session'),
    html.H1('Village Players Database Interface'),
    html.H2('Transactions - Insert'),
    html.Div(
        "Treasurer access only", id='a-transactions-no-access',
        hidden=False
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
            html.Label("New Member: "),
            dcc.Input(id='a-transactions-new-1', type='text'),
            # html.Label("New Member 2: "),
            # dcc.Input(id='a-transactions-new-2', type='text'),
            # html.Label("New Member 3: "),
            # dcc.Input(id='a-transactions-new-3', type='text'),
            # html.Label("Existing Member: "),
            # dcc.Dropdown(id='a-transactions-existing', options=[]),
            html.Label("Production: "),
            dcc.Dropdown(id='a-transactions-production', options=[]),
            html.Div(id='a-transactions-message'),
            html.Button("Insert New Transaction", id='a-transactions-insert'),
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
