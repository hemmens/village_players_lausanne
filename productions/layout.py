from current_role import current_role
from productions.callbacks import (
    register_productions_insert_callbacks, register_productions_lookup_callbacks,
    register_productions_update_callbacks, register_festivals_insert_callbacks
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
                # dag.AgGrid(
                #     id='f-productions-costs',
                #     columnDefs=[
                #         {'field': 'date', 'width': 200},
                #         {'field': 'amount', 'width': 150},
                #         {'field': 'recipient', 'width': 300},
                #         {'field': 'description', 'flex': 1},
                #     ]
                # ),
                html.A(
                    html.Button("Insert Production", id='f-productions-production-insert'), href='/productions/production-insert/'
                ),
                html.A(
                    html.Button("Insert Festival", id='f-productions-festival-insert'), href='/productions/festival-insert/'
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


def create_festivals_insert_app(server):
    app = Dash(
        __name__,
        server=server,
        url_base_pathname='/productions/festival-insert/',
    )

    role = current_role(server)

    app.layout = [
        dcc.Store(id='a-festivals-loaded', data=True),
        dcc.Store(id='a-festivals-role', storage_type='session', data=role),
        html.H1('Village Players Database Interface'),
        html.H2('Festivals - Insert'),
        html.Div(
            "Committee access only", id='a-festivals-no-access',
            hidden=(role in {"Committee", "Treasurer"})
        ),
        html.Div(
            [
                html.Label("Name: "),
                dcc.Input(id='a-festivals-name', type='text'),
                html.Label("Venue: "),
                dcc.Input(id='a-festivals-venue', type='text'),
                html.Label("Open Date: "),
                dcc.DatePickerSingle(id='a-festivals-open'),
                html.Label("Close Date: "),
                dcc.DatePickerSingle(id='a-festivals-close'),
                html.Div(id='a-festivals-message'),
                html.Button("Insert New Festival", id='a-festivals-insert'),
                html.A(
                    html.Button("Lookup", id='a-festivals-lookup'), href='/productions/lookup/'
                ),
                html.A(
                    html.Button("Insert Production", id='a-festivals-production-insert'), href='/productions/production-insert/'
                ),
                html.A(
                    html.Button("Update", id='a-festivals-update'), href='/productions/update/'
                ),
            ],
            id='a-festivals-access',
            hidden=(role not in {"Committee", "Treasurer"})
        ),
        html.A(
            html.Button("Home", id='a-festivals-home'), href='/'
        ),
    ]
    
    register_festivals_insert_callbacks(app, server)

    return app


def create_productions_insert_app(server):
    app = Dash(
        __name__,
        server=server,
        url_base_pathname='/productions/production-insert/',
    )

    role = current_role(server)

    app.layout = [
        dcc.Store(id='a-productions-loaded', data=True),
        dcc.Store(id='a-productions-role', storage_type='session', data=role),
        html.H1('Village Players Database Interface'),
        html.H2('Productions - Insert'),
        html.Div(
            "Committee access only", id='a-productions-no-access',
            hidden=(role in {"Committee", "Treasurer"})
        ),
        html.Div(
            [
                html.Label("Name: "),
                dcc.Input(id='a-productions-name', type='text'),
                html.Label("Venue: "),
                dcc.Input(id='a-productions-venue', type='text'),
                html.Label("Author: "),
                dcc.Input(id='a-productions-author', type='text'),
                html.Label("Open Date: "),
                dcc.DatePickerSingle(id='a-productions-open'),
                html.Label("Close Date: "),
                dcc.DatePickerSingle(id='a-productions-close'),
                html.Label("Festival: "),
                dcc.Dropdown(id='a-productions-festival', options=[]),
                html.Div(id='a-productions-message'),
                html.Button("Insert New Production", id='a-productions-insert'),
                html.A(
                    html.Button("Lookup", id='a-productions-lookup'), href='/productions/lookup/'
                ),
                html.A(
                    html.Button("Insert Festival", id='a-productions-festival-insert'), href='/productions/festival-insert/'
                ),
                html.A(
                    html.Button("Update", id='a-productions-update'), href='/productions/update/'
                ),
            ],
            id='a-productions-access',
            hidden=(role not in {"Committee", "Treasurer"})
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
        html.H2('Productions - Update'),
        html.Div(
            "Committee access only", id='u-productions-no-access',
            hidden=(role in {"Committee", "Treasurer"})
        ),
        html.Div(
            [
                html.Label("Select Production: "),
                dcc.Dropdown(id='u-productions-select', options=[], placeholder='Select Production'),
                html.Label("Venue: "),
                dcc.Input(id='u-productions-venue', type='text'),
                html.Label("Author: "),
                dcc.Input(id='u-productions-author', type='text'),
                html.Label("Open Date: "),
                dcc.DatePickerSingle(id='u-productions-open'),
                html.Label("Close Date: "),
                dcc.DatePickerSingle(id='u-productions-close'),
                html.Label("Festival: "),
                dcc.Dropdown(id='u-productions-festival', options=[]),
                html.Div(id='u-productions-message'),
                html.Button("Update Production", id='u-productions-update'),
                html.Button("Delete Production", id='u-productions-delete'),
                html.A(
                    html.Button("Lookup", id='u-productions-lookup'), href='/productions/lookup/'
                ),
                html.A(
                    html.Button("Insert Production", id='u-productions-production-insert'), href='/productions/production-insert/'
                ),
                html.A(
                    html.Button("Insert Festival", id='u-productions-festival-insert'), href='/productions/festival-insert/'
                ),
            ],
            id='u-productions-access',
            hidden=(role not in {"Committee", "Treasurer"})
        ),
        html.A(
            html.Button("Home", id='u-productions-home'), href='/'
        ),
    ]
    
    register_productions_update_callbacks(app, server)

    return app
