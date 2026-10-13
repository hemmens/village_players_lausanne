from current_role import current_role
from people.callbacks import register_people_insert_callbacks, register_people_update_callbacks
import variables

from dash import Dash, html, dcc


def create_people_insert_app(server):
    app = Dash(
        __name__,
        server=server,
        url_base_pathname='/people/insert/',
    )

    role = current_role(server)

    app.layout = [
        dcc.Store(id='a-people-loaded', data=True),
        dcc.Store(id='a-people-role', storage_type='session', data=role),
        html.H1('Village Players Database Interface'),
        html.H2('People - Insert'),
        html.Div(
            "Committee access only", id='a-people-no-access',
            hidden=(role in {"Committee", "Treasurer"})
        ),
        html.Div(
            [
                html.Label("First Name: "),
                dcc.Input(id='a-people-first-name', type='text'),
                html.Label("Surname: "),
                dcc.Input(id='a-people-surname', type='text'),
                html.Label("Address (first line): "),
                dcc.Input(id='a-people-address', type='text'),
                html.Label("Postcode: "),
                dcc.Input(id='a-people-postcode', type='text'),
                dcc.Checklist(
                    id='a-people-address-private',
                    options=[{'label': 'Address is Private', 'value': 'private'}]
                ),
                html.Label("Home Phone: "),
                dcc.Input(id='a-people-home-phone', type='text'),
                dcc.Checklist(
                    id='a-people-home-phone-private',
                    options=[{'label': 'Home Phone is Private', 'value': 'private'}]
                ),
                html.Label("Mobile: "),
                dcc.Input(id='a-people-mobile', type='text'),
                dcc.Checklist(
                    id='a-people-mobile-private',
                    options=[{'label': 'Mobile is Private', 'value': 'private'}]
                ),
                html.Label("Email: "),
                dcc.Input(id='a-people-email', type='text'),
                dcc.Checklist(
                    id='a-people-email-private',
                    options=[{'label': 'Email is Private', 'value': 'private'}]
                ),
                html.Label("Gender: "),
                dcc.Dropdown(id='a-people-gender', options=[
                    {'label': gender.title(), 'value': gender} for gender in [''] + variables.GENDERS
                ]),
                html.Label("GDPR Signed On: "),
                dcc.DatePickerSingle(id='a-people-gdpr'),
                html.Label("Committee Email: "),
                dcc.Input(id='a-people-committee-email', type='text'),
                html.Div(id='a-people-message'),
                html.Button("Insert New Person", id='a-people-insert'),
                html.A(
                    html.Button("Update", id='a-people-update'), href='/people/update/'
                ),
            ],
            id='a-people-access',
            hidden=(role not in {"Committee", "Treasurer"})
        ),
        html.A(
            html.Button("Home", id='a-people-home'), href='/'
        ),
    ]
    
    register_people_insert_callbacks(app, server)

    return app


def create_people_update_app(server):
    app = Dash(
        __name__,
        server=server,
        url_base_pathname='/people/update/',
    )

    role = current_role(server)

    app.layout = [
        dcc.Store(id='u-people-loaded', data=True),
        dcc.Store(id='u-people-role', storage_type='session', data=role),
        html.H1('Village Players Database Interface'),
        html.H2('People - Update'),
        html.Div(
            "Committee access only", id='u-people-no-access',
            hidden=(role in {"Committee", "Treasurer"})
        ),
        html.Div(
            [
                html.Label("Select Person to update: "),
                dcc.Dropdown(id='u-people-select', options=[], placeholder="Select a person"),
                html.Label("Address (first line): "),
                dcc.Input(id='u-people-address', type='text'),
                html.Label("Postcode: "),
                dcc.Input(id='u-people-postcode', type='text'),
                dcc.Checklist(
                    id='u-people-address-private',
                    options=[{'label': 'Address is Private', 'value': 'private'}]
                ),
                html.Label("Home Phone: "),
                dcc.Input(id='u-people-home-phone', type='text'),
                dcc.Checklist(
                    id='u-people-home-phone-private',
                    options=[{'label': 'Home Phone is Private', 'value': 'private'}]
                ),
                html.Label("Mobile: "),
                dcc.Input(id='u-people-mobile', type='text'),
                dcc.Checklist(
                    id='u-people-mobile-private',
                    options=[{'label': 'Mobile is Private', 'value': 'private'}]
                ),
                html.Label("Email: "),
                dcc.Input(id='u-people-email', type='text'),
                dcc.Checklist(
                    id='u-people-email-private',
                    options=[{'label': 'Email is Private', 'value': 'private'}]
                ),
                html.Label("Gender: "),
                dcc.Dropdown(id='u-people-gender', options=[
                    {'label': gender.title(), 'value': gender} for gender in [''] + variables.GENDERS
                ]),
                html.Label("GDPR Signed On: "),
                dcc.DatePickerSingle(id='u-people-gdpr'),
                html.Label("Committee Email: "),
                dcc.Input(id='u-people-committee-email', type='text'),
                html.Div(id='u-people-message'),
                html.Button("Update Person", id='u-people-update'),
                html.Button("Delete Person", id='u-people-delete'),
                html.A(
                    html.Button("Insert", id='u-people-insert'), href='/people/insert/'
                ),
            ],
            id='u-people-access',
            hidden=(role not in {"Committee", "Treasurer"})
        ),
        html.A(
            html.Button("Home", id='u-people-home'), href='/'
        ),
    ]
    
    register_people_update_callbacks(app, server)

    return app
