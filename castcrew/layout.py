from current_role import current_role
from castcrew.callbacks import register_castcrew_insert_callbacks, register_castcrew_update_callbacks
import variables

from dash import Dash, html, dcc


def create_castcrew_insert_app(server):
    app = Dash(
        __name__,
        server=server,
        url_base_pathname='/castcrew/insert/',
    )

    role = current_role(server)

    app.layout = [
        dcc.Store(id='a-castcrew-loaded', data=True),
        dcc.Store(id='a-castcrew-role', storage_type='session', data=role),
        html.H1('Village Players Database Interface'),
        html.H2('Cast & Crew - Insert'),
        html.Div(
            "Committee access only", id='a-castcrew-no-access',
            hidden=(role in {"Committee", "Treasurer"})
        ),
        html.Div(
            [
                html.Label("Person: "),
                dcc.Dropdown(id='a-castcrew-person', options=[]),
                html.Label("Production: "),
                dcc.Dropdown(id='a-castcrew-production', options=[]),
                html.Label("Role: "),
                dcc.Dropdown(id='a-castcrew-position', options=variables.ROLE_TYPES),
                html.Label("Character Name: "),
                dcc.Input(id='a-castcrew-role-name', type='text'),
                html.Div(id='a-castcrew-message'),
                html.Button("Insert New Cast or Crew Member", id='a-castcrew-insert'),
                html.A(
                    html.Button("Update", id='a-castcrew-update'), href='/castcrew/update/'
                ),
            ],
            id='a-castcrew-access',
            hidden=(role not in {"Committee", "Treasurer"})
        ),
        html.A(
            html.Button("Home", id='a-castcrew-home'), href='/'
        ),
    ]
    
    register_castcrew_insert_callbacks(app, server)

    return app


def create_castcrew_update_app(server):
    app = Dash(
        __name__,
        server=server,
        url_base_pathname='/castcrew/update/',
    )

    role = current_role(server)

    app.layout = [
        dcc.Store(id='u-castcrew-loaded', data=True),
        dcc.Store(id='u-castcrew-role', storage_type='session', data=role),
        html.H1('Village Players Database Interface'),
        html.H2('Cast & Crew - Update'),
        html.Div(
            "Committee access only", id='u-castcrew-no-access',
            hidden=(role in {"Committee", "Treasurer"})
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
            hidden=(role not in {"Committee", "Treasurer"})
        ),
        html.A(
            html.Button("Home", id='u-castcrew-home'), href='/'
        ),
    ]
    
    register_castcrew_update_callbacks(app, server)

    return app
