from datetime import date, timedelta

from dash import html, dcc
import dash_ag_grid as dag

from variables import SEASONS

FIRST_YEAR = int(SEASONS[-1][:4])
TODAY = date.today()

# balance_lookup_layout = [
#     dcc.Store(id='f-balance-loaded', data=True),
#     dcc.Store(id='f-balance-role', storage_type='session'),
#     html.H1('Village Players Database Interface'),
#     html.H2('Balance'),
#     html.Label("Amount: "),
#     dcc.Dropdown(id='f-balance-seasons', multi=True, options=SEASONS, value=[SEASONS[0]]),
#     dag.AgGrid(
#         id='f-balance-list',
#         columnDefs=[
#             {'field': 'season', 'headerName': 'Season'},
#             {'field': 'position', 'headerName': 'Position'},
#             {'field': 'full_name', 'headerName': 'Name'},
#             {'field': 'balance_email', 'headerName': 'Email'},
#         ]
#     ),
#     html.Div(
#         [
#             html.A(
#                 html.Button("Insert", id='f-balance-insert'), href='/balance/insert/'
#             ),
#             html.A(
#                 html.Button("Update", id='f-balance-update'), href='/balance/update/'
#             ),
#         ],
#         id='f-balance-access',
#         hidden=True
#     ),
#     html.A(
#         html.Button("Home", id='f-balance-home'), href='/'
#     ),
# ]

balance_insert_layout = [
    dcc.Store(id='a-balance-loaded', data=True),
    dcc.Store(id='a-balance-role', storage_type='session'),
    html.H1('Village Players Database Interface'),
    html.H2('Balance - Insert'),
    html.Div(
        "Treasurer access only", id='a-balance-no-access',
        hidden=False
    ),
    html.Div(
        [
            html.Label("Amount: "),
            dcc.Input(id='a-balance-amount', type='number'),
            html.Label("Month: "),
            dcc.Dropdown(
                id='a-balance-month',
                options=[
                    {'label': 'January', 'value': 1},
                    {'label': 'February', 'value': 2},
                    {'label': 'March', 'value': 3},
                    {'label': 'April', 'value': 4},
                    {'label': 'May', 'value': 5},
                    {'label': 'June', 'value': 6},
                    {'label': 'July', 'value': 7},
                    {'label': 'August', 'value': 8},
                    {'label': 'September', 'value': 9},
                    {'label': 'October', 'value': 10},
                    {'label': 'November', 'value': 11},
                    {'label': 'December', 'value': 12},
                ],
                value=(TODAY - timedelta(10)).month
            ),
            html.Label("Year: "),
            dcc.Dropdown(
                id='a-balance-year',
                options=list(range(FIRST_YEAR, (TODAY.year + 1))),
                value=(TODAY - timedelta(10)).year
            ),
            html.Div(id='a-balance-message'),
            html.Button("Insert New Balance Amount", id='a-balance-insert'),
            # html.A(
            #     html.Button("Lookup", id='a-balance-lookup'), href='/balance/lookup/'
            # ),
            # html.A(
            #     html.Button("Update", id='a-balance-update'), href='/balance/update/'
            # ),
        ],
        id='a-balance-access',
        hidden=True
    ),
    html.A(
        html.Button("Home", id='a-balance-home'), href='/'
    ),
]

# balance_update_layout = [
#     dcc.Store(id='u-balance-loaded', data=True),
#     dcc.Store(id='u-balance-role', storage_type='session'),
#     html.H1('Village Players Database Interface'),
#     html.H2('balance - Update'),
#     html.Div(
#         "balance access only", id='u-balance-no-access',
#         hidden=False
#     ),
#     html.Div(
#         [
#             html.Label("Select balance Position: "),
#             dcc.Dropdown(id='u-balance-position', options=[]),
#             html.Div(id='u-balance-message'),
#             html.Button("Delete balance Member", id='u-balance-delete'),
#             html.A(
#                 html.Button("Lookup", id='u-balance-lookup'), href='/balance/lookup/'
#             ),
#             html.A(
#                 html.Button("Insert", id='u-balance-insert'), href='/balance/insert/'
#             ),
#         ],
#         id='u-balance-access',
#         hidden=True
#     ),
#     html.A(
#         html.Button("Home", id='u-balance-home'), href='/'
#     ),
# ]
