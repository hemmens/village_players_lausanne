from current_role import current_role
from committee.callbacks import register_committee_lookup_callbacks
import variables

from dash import Dash, html, dcc
import dash_ag_grid as dag

seasons = variables.SEASONS
mtypes = variables.MEMBER_TYPES
mcols = list(variables.MEMBER_LIST_COLUMNS.keys())

def create_committee_app(server):
    app = Dash(
        __name__,
        server=server,
        url_base_pathname='/committee/',
    )

    role = current_role(server)

    app.layout = [
        dcc.Store(id='f-committee-loaded', data=True),
        dcc.Store(id='f-committee-role', storage_type='session', data=role),
        html.H1('Village Players Database Interface'),
        html.H2('Committee'),
        html.Label("Select Seasons: ", id='f-committee-seasons-label'),
        dcc.Dropdown(id='f-committee-seasons', multi=True, options=seasons, value=[seasons[0]]),
        dag.AgGrid(
            id='f-committee-list',
            columnDefs=[
                {'field': 'season', 'headerName': 'Season'},
                {'field': 'position', 'headerName': 'Position'},
                {'field': 'first_name', 'headerName': 'First Name'},
                {'field': 'surname', 'headerName': 'Surname'},
                {'field': 'committee_email', 'headerName': 'Email'},
            ]
        ),
        html.Button("Update", id='f-committee-update', style={'display': 'none'} if role == "Public" else {}),
        html.Button("Insert", id='f-committee-insert', style={'display': 'none'} if role == "Public" else {}),
    ]
    
    register_committee_lookup_callbacks(app, server)

    return app
