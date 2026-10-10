from current_role import current_role
from committee.callbacks import (
    register_committee_insert_callbacks, register_committee_lookup_callbacks,
    register_committee_update_callbacks
)
import variables

from dash import Dash, html, dcc
import dash_ag_grid as dag

seasons = variables.SEASONS

def create_committee_lookup_app(server):
    app = Dash(
        __name__,
        server=server,
        url_base_pathname='/committee/lookup/',
    )

    role = current_role(server)

    app.layout = [
        dcc.Store(id='f-committee-loaded', data=True),
        dcc.Store(id='f-committee-role', storage_type='session', data=role),
        html.H1('Village Players Database Interface'),
        html.H2('Committee'),
        html.Label("Select Seasons: "),
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
            hidden=(role not in {"Committee", "Treasurer"})
        ),
        html.A(
            html.Button("Home", id='f-committee-home'), href='/'
        ),
        
    ]
    
    register_committee_lookup_callbacks(app, server)

    return app


def create_committee_insert_app(server):
    app = Dash(
        __name__,
        server=server,
        url_base_pathname='/committee/insert/',
    )

    role = current_role(server)

    app.layout = [
        dcc.Store(id='a-committee-loaded', data=True),
        dcc.Store(id='a-committee-role', storage_type='session', data=role),
        html.H1('Village Players Database Interface'),
        html.H2('Committee - Insert'),
        html.Div(
            "Committee access only", id='a-committee-no-access',
            hidden=(role in {"Committee", "Treasurer"})
        ),
        html.Div(
            [
                html.Label("Select Person: "),
                dcc.Dropdown(id='a-committee-person', options=[]),
                html.Label("Select Season: "),
                dcc.Dropdown(id='a-committee-season', options=seasons),
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
            hidden=(role not in {"Committee", "Treasurer"})
        ),
        html.A(
            html.Button("Home", id='a-committee-home'), href='/'
        ),
    ]
    
    register_committee_insert_callbacks(app, server)

    return app


def create_committee_update_app(server):
    app = Dash(
        __name__,
        server=server,
        url_base_pathname='/committee/update/',
    )

    role = current_role(server)

    app.layout = [
        dcc.Store(id='u-committee-loaded', data=True),
        dcc.Store(id='u-committee-role', storage_type='session', data=role),
        html.H1('Village Players Database Interface'),
        html.H2('Committee - Update'),
        html.Div(
            "Committee access only", id='u-committee-no-access',
            hidden=(role in {"Committee", "Treasurer"})
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
            hidden=(role not in {"Committee", "Treasurer"})
        ),
        html.A(
            html.Button("Home", id='u-committee-home'), href='/'
        ),
    ]
    
    register_committee_update_callbacks(app, server)

    return app
