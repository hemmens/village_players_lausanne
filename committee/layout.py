from dash import html, dcc
import dash_ag_grid as dag

from variables import SEASONS

committee_lookup_layout = [
    dcc.Store(id='f-committee-loaded', data=True),
    dcc.Store(id='f-committee-role', storage_type='session'),
    html.H1('Village Players Database Interface'),
    html.H2('Committee'),
    html.Label("Select Seasons: "),
    dcc.Dropdown(id='f-committee-seasons', multi=True, options=SEASONS, value=[SEASONS[0]]),
    dag.AgGrid(
        id='f-committee-list',
        columnDefs=[
            {'field': 'season', 'headerName': 'Season'},
            {'field': 'position', 'headerName': 'Position'},
            {'field': 'full_name', 'headerName': 'Name'},
            {'field': 'committee_email', 'headerName': 'Email'},
        ]
    ),
    html.Div(
        [
            html.A(
                html.Button("Insert", id='f-committee-insert'), href='/committee/insert/'
            ),
            html.A(
                html.Button("Update", id='f-committee-update'), href='/committee/update/'
            ),
        ],
        id='f-committee-access',
        hidden=True
    ),
    html.A(
        html.Button("Home", id='f-committee-home'), href='/'
    ),
]

committee_insert_layout = [
    dcc.Store(id='a-committee-loaded', data=True),
    dcc.Store(id='a-committee-role', storage_type='session'),
    html.H1('Village Players Database Interface'),
    html.H2('Committee - Insert'),
    html.Div(
        "Committee access only", id='a-committee-no-access',
        hidden=False
    ),
    html.Div(
        [
            html.Label("Select Person: "),
            dcc.Dropdown(id='a-committee-person', options=[]),
            html.Label("Select Season: "),
            dcc.Dropdown(id='a-committee-season', options=SEASONS),
            html.Label("Position: "),
            dcc.Input(id='a-committee-position', type='text'),
            html.Div(id='a-committee-message'),
            html.Button("Insert New Committee Member", id='a-committee-insert'),
            html.A(
                html.Button("Lookup", id='a-committee-lookup'), href='/committee/lookup/'
            ),
            html.A(
                html.Button("Update", id='a-committee-update'), href='/committee/update/'
            ),
        ],
        id='a-committee-access',
        hidden=True
    ),
    html.A(
        html.Button("Home", id='a-committee-home'), href='/'
    ),
]

committee_update_layout = [
    dcc.Store(id='u-committee-loaded', data=True),
    dcc.Store(id='u-committee-role', storage_type='session'),
    html.H1('Village Players Database Interface'),
    html.H2('Committee - Update'),
    html.Div(
        "Committee access only", id='u-committee-no-access',
        hidden=False
    ),
    html.Div(
        [
            html.Label("Select Committee Position: "),
            dcc.Dropdown(id='u-committee-position', options=[]),
            html.Div(id='u-committee-message'),
            html.Button("Delete Committee Member", id='u-committee-delete'),
            html.A(
                html.Button("Lookup", id='u-committee-lookup'), href='/committee/lookup/'
            ),
            html.A(
                html.Button("Insert", id='u-committee-insert'), href='/committee/insert/'
            ),
        ],
        id='u-committee-access',
        hidden=True
    ),
    html.A(
        html.Button("Home", id='u-committee-home'), href='/'
    ),
]
