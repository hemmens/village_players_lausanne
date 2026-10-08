from current_role import current_role
from members.callbacks import register_member_callbacks
import variables

from dash import Dash, html, dcc
import dash_ag_grid as dag

seasons = variables.SEASONS
mtypes = variables.MEMBER_TYPES
mcols = list(variables.MEMBER_LIST_COLUMNS.keys())

def create_members_app(server):
    app = Dash(
        __name__,
        server=server,
        url_base_pathname='/members/',
    )

    role = current_role(server)

    app.layout = [
        dcc.Store(id='f-member-loaded', data=True),
        dcc.Store(id='f-member-role', storage_type='session', data=role),
        html.H1('Village Players Database Interface'),
        html.H2('Members'),
        dcc.Download(id='f-member-download'),
        html.Label("Select Seasons: ", id='f-member-seasons-label'),
        dcc.Dropdown(id='f-member-seasons', multi=True, options=seasons, value=[seasons[0]]),
        html.Label(
            "Select Membership Types: ", id='f-member-types-label', hidden=(role == "Public")
        ),
        dcc.Dropdown(
            id='f-member-types', multi=True, options=mtypes, value=mtypes,
            style={'display': 'none'} if role == "Public" else {}
        ),
        html.Label("Select People: ", id='f-member-persons-label'),
        dcc.Dropdown(id='f-member-persons', multi=True, options=[], value=[]),
        html.Label("Select Columns: ", id='f-member-columns-label', hidden=(role == "Public")),
        dcc.Dropdown(
            id='f-member-columns', multi=True, options=mcols,
            value=['Season', 'First Name', 'Surname'],
            style={'display': 'none'} if role == "Public" else {}
        ),
        dag.AgGrid(
            id='f-member-list',
            columnDefs=[
                {'field': 'season', 'headerName': 'Season'}, 
                {'field': 'first_name', 'headerName': 'First Name'}, 
                {'field': 'surname', 'headerName': 'Surname'},
            ]
        ),
        html.Button("Export to Excel", id='f-member-button'),
    ]
    
    register_member_callbacks(app, server)

    return app
