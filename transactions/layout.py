from current_role import current_role
from transactions.callbacks import register_transactions_insert_callbacks
import variables

from dash import Dash, html, dcc


def create_transactions_insert_app(server):
    app = Dash(
        __name__,
        server=server,
        url_base_pathname='/transactions/insert/',
    )

    role = current_role(server)

    app.layout = [
        dcc.Store(id='a-transactions-loaded', data=True),
        dcc.Store(id='a-transactions-role', storage_type='session', data=role),
        html.H1('Village Players Database Interface'),
        html.H2('Transactions - Insert'),
        html.Div(
            "Treasurer access only", id='a-transactions-no-access',
            hidden=(role == "Treasurer")
        ),
        html.Div(
            [
                html.Label("Transaction Type: "),
                dcc.Dropdown(id='a-transactions-type', options=variables.TRANS_TYPES),
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
                dcc.Dropdown(id='a-transactions-member-type', options=variables.MEMBER_TYPES),
                html.Label("Renewing Member: "),
                dcc.Dropdown(id='a-transactions-renew', options=[]),
                html.Label("New Member 1: "),
                dcc.Input(id='a-transactions-new-1', type='text'),
                html.Label("New Member 2: "),
                dcc.Input(id='a-transactions-new-2', type='text'),
                html.Label("New Member 3: "),
                dcc.Input(id='a-transactions-new-3', type='text'),
                html.Label("Existing Member: "),
                dcc.Dropdown(id='a-transactions-existing', options=[]),
                html.Label("Production: "),
                dcc.Dropdown(id='a-transactions-production', options=[]),
                html.Div(id='a-transactions-message'),
                html.Button("Insert New Transaction", id='a-transactions-insert'),
                # html.A(
                #     html.Button("Update", id='a-transactions-update'), href='/transactions/update/'
                # ),
            ],
            id='a-transactions-access',
            hidden=(role != "Treasurer")
        ),
        html.A(
            html.Button("Home", id='a-transactions-home'), href='/'
        ),
    ]
    
    register_transactions_insert_callbacks(app, server)

    return app


# def create_transactions_update_app(server):
#     app = Dash(
#         __name__,
#         server=server,
#         url_base_pathname='/transactions/update/',
#     )

#     role = current_role(server)

#     app.layout = [
#         dcc.Store(id='u-transactions-loaded', data=True),
#         dcc.Store(id='u-transactions-role', storage_type='session', data=role),
#         html.H1('Village Players Database Interface'),
#         html.H2('Cast & Crew - Update'),
#         html.Div(
#             "Committee access only", id='u-transactions-no-access',
#             hidden=(role in {"Committee", "Treasurer"})
#         ),
#         html.Div(
#             [
#                 html.Label("Select Cast or Crew to update: "),
#                 dcc.Dropdown(id='u-transactions-select', options=[], placeholder="Select a role"),
#                 html.Label("Character: "),
#                 dcc.Input(id='u-transactions-role-name', type='text'),
#                 html.Div(id='u-transactions-message'),
#                 html.Button("Update Person", id='u-transactions-update'),
#                 html.Button("Delete Person", id='u-transactions-delete'),
#                 html.A(
#                     html.Button("Insert", id='u-transactions-insert'), href='/transactions/insert/'
#                 ),
#             ],
#             id='u-transactions-access',
#             hidden=(role not in {"Committee", "Treasurer"})
#         ),
#         html.A(
#             html.Button("Home", id='u-transactions-home'), href='/'
#         ),
#     ]
    
#     register_transactions_update_callbacks(app, server)

#     return app
