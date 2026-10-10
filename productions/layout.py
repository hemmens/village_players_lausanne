from current_role import current_role
from productions.callbacks import (
    register_productions_insert_callbacks, register_productions_lookup_callbacks,
    register_productions_update_callbacks
)
import variables

from dash import Dash, html, dcc
import dash_ag_grid as dag

def create_productions_lookup_app(server):
    app = Dash(
        __name__,
        server=server,
        url_base_pathname='/productions/lookup/',
    )

    role = current_role(server)

    app.layout = [
        dcc.Store(id='f-productions-loaded', data=True),
        dcc.Store(id='f-productions-role', storage_type='session', data=role),
        html.H1('Village Players Database Interface'),
        html.H2('Productions'),
        html.Label("Select Production: "),
        dcc.Dropdown(id='f-productions-select', options=[], placeholder='Select Production'),
        dag.AgGrid(
            id='f-productions-details',
            columnDefs=[
                {'field': 'detail', 'width': 200},
                {'field': 'info', 'flex': 1},
            ],
            dashGridOptions={
                'headerHeight': 0,
            }
        ),
        html.Div(
            [
                dag.AgGrid(
                    id='f-productions-costs',
                    columnDefs=[
                        {'field': 'date', 'width': 200},
                        {'field': 'amount', 'width': 150},
                        {'field': 'recipient', 'width': 300},
                        {'field': 'description', 'flex': 1},
                    ]
                ),
                html.A(
                    html.Button("Insert", id='f-productions-insert'), href='/productions/insert/'
                ),
                html.A(
                    html.Button("Update", id='f-productions-update'), href='/productions/update/'
                ),
            ],
            id='f-productions-access',
            hidden=(role not in {"productions", "Treasurer"})
        ),
        html.A(
            html.Button("Home", id='f-productions-home'), href='/'
        ),
        
    ]
    
    register_productions_lookup_callbacks(app, server)

    return app


def create_productions_insert_app(server):
    app = Dash(
        __name__,
        server=server,
        url_base_pathname='/productions/insert/',
    )

    role = current_role(server)

    app.layout = [
        dcc.Store(id='a-productions-loaded', data=True),
        dcc.Store(id='a-productions-role', storage_type='session', data=role),
        html.H1('Village Players Database Interface'),
        html.H2('productions - Insert'),
        html.Div(
            "productions access only", id='a-productions-no-access',
            hidden=(role in {"productions", "Treasurer"})
        ),
        html.Div(
            [
                html.Label("Select Person: ", id='a-productions-person-label'),
                dcc.Dropdown(id='a-productions-person', options=[]),
                html.Label("Select Season: ", id='a-productions-season-label'),
                dcc.Dropdown(id='a-productions-season', options=seasons),
                html.Label("Position: ", id='a-productions-position-label'),
                dcc.Input(id='a-productions-position', type='text'),
                html.Div(id='a-productions-message'),
                html.Button("Insert New productions Member", id='a-productions-insert'),
                html.A(
                    html.Button("Lookup", id='a-productions-lookup'), href='/productions/lookup/'
                ),
                html.A(
                    html.Button("Update", id='a-productions-update'), href='/productions/update/'
                ),
            ],
            id='a-productions-access',
            hidden=(role not in {"productions", "Treasurer"})
        ),
        html.A(
            html.Button("Home", id='a-productions-home'), href='/'
        ),
    ]
    
    register_productions_insert_callbacks(app, server)

    return app


def create_productions_update_app(server):
    app = Dash(
        __name__,
        server=server,
        url_base_pathname='/productions/update/',
    )

    role = current_role(server)

    app.layout = [
        dcc.Store(id='u-productions-loaded', data=True),
        dcc.Store(id='u-productions-role', storage_type='session', data=role),
        html.H1('Village Players Database Interface'),
        html.H2('productions - Update'),
        html.Div(
            "productions access only", id='u-productions-no-access',
            hidden=(role in {"productions", "Treasurer"})
        ),
        html.Div(
            [
                html.Label("Select productions Position: ", id='u-productions-label'),
                dcc.Dropdown(id='u-productions-position', options=[]),
                html.Div(id='u-productions-message'),
                html.Button("Delete productions Member", id='u-productions-delete'),
                html.A(
                    html.Button("Lookup", id='u-productions-lookup'), href='/productions/lookup/'
                ),
                html.A(
                    html.Button("Insert", id='u-productions-insert'), href='/productions/insert/'
                ),
            ],
            id='u-productions-access',
            hidden=(role not in {"productions", "Treasurer"})
        ),
        html.A(
            html.Button("Home", id='u-productions-home'), href='/'
        ),
    ]
    
    register_productions_update_callbacks(app, server)

    return app
