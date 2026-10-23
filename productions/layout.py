from dash import html, dcc
import dash_ag_grid as dag

productions_lookup_layout = [
    dcc.Store(id='f-productions-loaded', data=True),
    dcc.Store(id='f-productions-role', storage_type='session'),
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
                html.Button("Insert Production", id='f-productions-insert'), href='/productions/insert/'
            ),
            html.A(
                html.Button("Update", id='f-productions-update'), href='/productions/update/'
            ),
        ],
        id='f-productions-access',
        hidden=True
    ),
    html.A(
        html.Button("Home", id='f-productions-home'), href='/'
    ),
]

productions_insert_layout = [
    dcc.Store(id='a-productions-loaded', data=True),
    dcc.Store(id='a-productions-role', storage_type='session'),
    html.H1('Village Players Database Interface'),
    html.H2('Productions - Insert'),
    html.Div(
        "Committee access only", id='a-productions-no-access',
        hidden=False
    ),
    html.Div(
        [
            html.Label("Type: "),
            dcc.Dropdown(
                id='a-productions-type', options=['Production', 'Festival'], value='Production'
            ),
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
                html.Button("Update", id='a-productions-update'), href='/productions/update/'
            ),
        ],
        id='a-productions-access',
        hidden=True
    ),
    html.A(
        html.Button("Home", id='a-productions-home'), href='/'
    ),
]

productions_update_layout = [
    dcc.Store(id='u-productions-loaded', data=True),
    dcc.Store(id='u-productions-role', storage_type='session'),
    html.H1('Village Players Database Interface'),
    html.H2('Productions - Update'),
    html.Div(
        "Committee access only", id='u-productions-no-access',
        hidden=False
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
                html.Button("Insert Production", id='u-productions-insert'), href='/productions/insert/'
            ),
        ],
        id='u-productions-access',
        hidden=True
    ),
    html.A(
        html.Button("Home", id='u-productions-home'), href='/'
    ),
]
