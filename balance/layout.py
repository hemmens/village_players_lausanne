from datetime import date, timedelta

from dash import html, dcc
import dash_ag_grid as dag

from balance.database import MONTHS
from variables import SEASONS

FIRST_YEAR = int(SEASONS[-1][:4])
TODAY = date.today()
MONTHS = [{'label': mth_str, 'value': mth_int} for mth_int, mth_str in MONTHS.items()]
YEARS = list(range(FIRST_YEAR, (TODAY.year + 1)))

balance_lookup_layout = [
    dcc.Store(id='f-balance-loaded', data=True),
    dcc.Store(id='f-balance-role', storage_type='session'),
    html.H1('Village Players Database Interface'),
    html.H2('Balance'),
    html.Div(
        "Committee access only", id='f-balance-no-access', hidden=False
    ),
    html.Div(
        [
            html.Label("Month: "),
            dcc.Dropdown(id='f-balance-month', multi=True, options=MONTHS),
            html.Label("Year: "),
            dcc.Dropdown(id='f-balance-year', multi=True, options=YEARS),
            html.Label("Start Date: "),
            dcc.DatePickerSingle(id='f-balance-start-date', clearable=True),
            html.Label("End Date: "),
            dcc.DatePickerSingle(id='f-balance-end-date', clearable=True),
            dag.AgGrid(
                id='f-balance-list',
                columnDefs=[
                    {'field': 'month', 'width': 150},
                    {'field': 'year', 'width': 150},
                    {'field': 'amount', 'width': 150},
                    {'field': 'difference', 'width': 150},
                ]
            ),
        ],
        id='f-balance-access',
        hidden=True
    ),
    html.Div(
        [
            html.A(
                html.Button("Insert", id='f-balance-insert'), href='/balance/insert/'
            ),
            # html.A(
            #     html.Button("Update", id='f-balance-update'), href='/balance/update/'
            # ),
        ],
        id='f-balance-treasurer-access',
        hidden=True
    ),
    html.A(
        html.Button("Home", id='f-balance-home'), href='/'
    ),
]

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
                options=MONTHS,
                value=(TODAY - timedelta(10)).month
            ),
            html.Label("Year: "),
            dcc.Dropdown(
                id='a-balance-year',
                options=YEARS,
                value=(TODAY - timedelta(10)).year
            ),
            html.Div(id='a-balance-message'),
            html.Button("Insert New Balance Amount", id='a-balance-insert'),
            html.A(
                html.Button("Lookup", id='a-balance-lookup'), href='/balance/lookup/'
            ),
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
