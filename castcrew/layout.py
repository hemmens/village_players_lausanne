from dash import html, dcc

from variables import ROLE_TYPES

castcrew_insert_layout = [
    dcc.Store(id='a-castcrew-loaded', data=True),
    dcc.Store(id='a-castcrew-role', storage_type='session'),
    html.H1('Village Players Database Interface'),
    html.H2('Cast & Crew - Insert'),
    html.Div(
        "Committee access only", id='a-castcrew-no-access',
        hidden=False
    ),
    html.Div(
        [
            html.Label("Person: "),
            dcc.Dropdown(id='a-castcrew-person', options=[]),
            html.Label("Production: "),
            dcc.Dropdown(id='a-castcrew-production', options=[]),
            html.Label("Role: "),
            dcc.Dropdown(id='a-castcrew-position', options=ROLE_TYPES),
            html.Label("Character Name: "),
            dcc.Input(id='a-castcrew-role-name', type='text'),
            html.Div(id='a-castcrew-message'),
            html.Button("Insert New Cast or Crew Member", id='a-castcrew-insert'),
            html.A(
                html.Button("Update", id='a-castcrew-update'), href='/castcrew/update/'
            ),
        ],
        id='a-castcrew-access',
        hidden=True
    ),
    html.A(
        html.Button("Home", id='a-castcrew-home'), href='/'
    ),
]

castcrew_update_layout = [
    dcc.Store(id='u-castcrew-loaded', data=True),
    dcc.Store(id='u-castcrew-role', storage_type='session'),
    html.H1('Village Players Database Interface'),
    html.H2('Cast & Crew - Update'),
    html.Div(
        "Committee access only", id='u-castcrew-no-access',
        hidden=False
    ),
    html.Div(
        [
            html.Label("Select Cast or Crew to update: "),
            dcc.Dropdown(id='u-castcrew-select', options=[], placeholder="Select a role"),
            html.Label("Character: "),
            dcc.Input(id='u-castcrew-role-name', type='text'),
            html.Div(id='u-castcrew-message'),
            html.Button("Update Person", id='u-castcrew-update'),
            html.Button("Delete Person", id='u-castcrew-delete'),
            html.A(
                html.Button("Insert", id='u-castcrew-insert'), href='/castcrew/insert/'
            ),
        ],
        id='u-castcrew-access',
        hidden=True
    ),
    html.A(
        html.Button("Home", id='u-castcrew-home'), href='/'
    ),
]
