from dash import html, dcc

newsletters_lookup_layout = [
    dcc.Store(id='f-newsletters-loaded', data=True),
    dcc.Store(id='f-newsletters-role', storage_type='session'),
    html.H1('Village Players Database Interface'),
    html.H2('Newsletters'),
    html.Label("Select Newsletter: "),
    dcc.Dropdown(id='f-newsletters-select', options=[], placeholder='Select Newsletter'),
    html.Div(
        html.Iframe(id='f-newsletters-pdf', style={'height': '297mm', 'width': '210mm'})
    ),
    html.Div(
        [
            html.A(
                html.Button("Insert", id='f-newsletters-insert'), href='/newsletters/insert/'
            ),
            html.A(
                html.Button("Update", id='f-newsletters-update'), href='/newsletters/update/'
            ),
        ],
        id='f-newsletters-access',
        hidden=True
    ),
    html.A(
        html.Button("Home", id='f-newsletters-home'), href='/'
    ),
]

newsletters_insert_layout = [
    dcc.Store(id='a-newsletters-loaded', data=True),
    dcc.Store(id='a-newsletters-role', storage_type='session'),
    html.H1('Village Players Database Interface'),
    html.H2('Newsletters - Insert'),
    html.Div(
        "Committee access only", id='a-newsletters-no-access',
        hidden=False
    ),
    html.Div(
        [
            html.Label("Sent Date: "),
            dcc.DatePickerSingle(id='a-newsletters-sent'),
            html.Label("URL: "),
            dcc.Input(id='a-newsletters-url', type='url'),
            html.Label("Name (optional): "),
            dcc.Input(id='a-newsletters-name', type='text'),
            html.Div(id='a-newsletters-message'),
            html.Button("Insert New Newsletter", id='a-newsletters-insert'),
            html.A(
                html.Button("Lookup", id='a-newsletters-lookup'), href='/newsletters/lookup/'
            ),
            html.A(
                html.Button("Update", id='a-newsletters-update'), href='/newsletters/update/'
            ),
        ],
        id='a-newsletters-access',
        hidden=True
    ),
    html.A(
        html.Button("Home", id='a-newsletters-home'), href='/'
    ),
]

newsletters_update_layout = [
    dcc.Store(id='u-newsletters-loaded', data=True),
    dcc.Store(id='u-newsletters-role', storage_type='session'),
    html.H1('Village Players Database Interface'),
    html.H2('Newsletters - Update'),
    html.Div(
        "Committee access only", id='u-newsletters-no-access',
        hidden=False
    ),
    html.Div(
        [
            html.Label("Select Newsletter: "),
            dcc.Dropdown(id='u-newsletters-select', options=[], placeholder='Select Newsletter'),
            html.Label("Sent Date: "),
            dcc.DatePickerSingle(id='u-newsletters-sent'),
            html.Label("URL: "),
            dcc.Input(id='u-newsletters-url', type='url'),
            html.Label("Name (optional): "),
            dcc.Input(id='u-newsletters-name', type='text'),
            html.Div(id='u-newsletters-message'),
            html.Button("Update Newsletter", id='u-newsletters-update'),
            html.A(
                html.Button("Lookup", id='u-newsletters-lookup'), href='/newsletters/lookup/'
            ),
            html.A(
                html.Button("Insert", id='u-newsletters-insert'), href='/newsletters/insert/'
            ),
        ],
        id='u-newsletters-access',
        hidden=True
    ),
    html.A(
        html.Button("Home", id='u-newsletters-home'), href='/'
    ),
]
