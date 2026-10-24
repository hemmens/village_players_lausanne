from dash import html, dcc
import dash_ag_grid as dag

from variables import MEMBER_LIST_COLUMNS, MEMBER_TYPES, SEASONS

mcols = list(MEMBER_LIST_COLUMNS.keys())

members_search_layout = [
    html.Label("First Name: "),
    dcc.Input(id='s-member-first-name', type='text'),
    html.Label("Surname: "),
    dcc.Input(id='s-member-surname', type='text'),
    html.Label("Email: "),
    dcc.Input(id='s-member-email', type='text'),
    html.Label("Season: "),
    dcc.Dropdown(id='s-member-season', options=SEASONS, value=SEASONS[0]),
    html.Div(id='s-member-message'),
    html.Button("Search", id='s-member-search'),
    html.A(html.Button("Home", id='s-member-home'), href='/'),
]

members_lookup_layout = [
    dcc.Store(id='f-member-loaded', data=True),
    dcc.Store(id='f-member-role', storage_type='session'),
    html.H1('Village Players Database Interface'),
    html.H2('Members'),
    dcc.Download(id='f-member-download'),
    html.Label("Select Seasons: "),
    dcc.Dropdown(id='f-member-seasons', multi=True, options=SEASONS, value=[SEASONS[0]]),
    html.Div(
        [
            html.Label("Select Membership Types: "),
            dcc.Dropdown(id='f-member-types', multi=True, options=MEMBER_TYPES, value=MEMBER_TYPES),
            html.Label("Select Columns: "),
            dcc.Dropdown(
                id='f-member-columns', multi=True, options=mcols,
                value=['Season', 'First Name', 'Surname']
            ),
        ],
        id='f-member-access',
        hidden=True
    ),
    html.Label("Select People: "),
    dcc.Dropdown(id='f-member-persons', multi=True, options=[], value=[]),
    dag.AgGrid(
        id='f-member-list',
        columnDefs=[
            {'field': 'season', 'headerName': 'Season'}, 
            {'field': 'first_name', 'headerName': 'First Name'}, 
            {'field': 'surname', 'headerName': 'Surname'},
        ]
    ),
    html.Button("Export to Excel", id='f-member-button'),
    html.A(
        html.Button("Home", id='f-member-home'), href='/'
    ),
]
