from current_role import current_role
from dash import Input, Output, State
from database import (
    get_festivals, get_productions, get_production_details, insert_festival, insert_production
)

def register_productions_lookup_callbacks(app, server):
    @app.callback(
        Output('f-productions-role', 'data'),
        Input('f-productions-loaded', 'data'),
    )
    def update_role(loaded):
        return current_role(server)
    
    @app.callback(
        Output('f-productions-access', 'hidden'),
        Input('f-productions-role', 'data'),
    )
    def update_access_hidden(role):
        return role not in {"Committee", "Treasurer"}

    @app.callback(
        Output('f-productions-select', 'options'),
        Input('f-productions-loaded', 'data'),
    )
    def update_productions(loaded):
        return get_productions()

    @app.callback(
        Output('f-productions-details', 'rowData'),
        Input('f-productions-select', 'value'),
    )
    def update_row_data(production_id):
        return get_production_details(production_id)


def register_festivals_insert_callbacks(app, server):
    @app.callback(
        Output('a-festivals-role', 'data'),
        Input('a-festivals-loaded', 'data'),
    )
    def update_role(loaded):
        return current_role(server)
    
    @app.callback(
        Output('a-festivals-access', 'hidden'),
        Input('a-festivals-role', 'data'),
    )
    def update_access_hidden(role):
        return role not in {"Committee", "Treasurer"}
    
    @app.callback(
        Output('a-festivals-no-access', 'hidden'),
        Input('a-festivals-role', 'data'),
    )
    def update_no_access_hidden(role):
        return role in {"Committee", "Treasurer"}

    @app.callback(
        Output('a-festivals-message', 'children'),
        Input('a-festivals-insert', 'n_clicks'),
        State('a-festivals-name', 'value'),
        State('a-festivals-venue', 'value'),
        State('a-festivals-open', 'date'),
        State('a-festivals-close', 'date'),
        prevent_initial_call=True
    )
    def new_festival(n_clicks, name, venue, open, close):
        return insert_festival(name, venue, open, close)


def register_productions_insert_callbacks(app, server):
    @app.callback(
        Output('a-productions-role', 'data'),
        Input('a-productions-loaded', 'data'),
    )
    def update_role(loaded):
        return current_role(server)
    
    @app.callback(
        Output('a-productions-access', 'hidden'),
        Input('a-productions-role', 'data'),
    )
    def update_access_hidden(role):
        return role not in {"Committee", "Treasurer"}
    
    @app.callback(
        Output('a-productions-no-access', 'hidden'),
        Input('a-productions-role', 'data'),
    )
    def update_no_access_hidden(role):
        return role in {"Committee", "Treasurer"}

    @app.callback(
        Output('a-productions-festival', 'options'),
        Input('a-productions-loaded', 'data'),
    )
    def update_festivals(loaded):
        return get_festivals()

    @app.callback(
        Output('a-productions-message', 'children'),
        Input('a-productions-insert', 'n_clicks'),
        State('a-productions-name', 'value'),
        State('a-productions-venue', 'value'),
        State('a-productions-author', 'value'),
        State('a-productions-open', 'date'),
        State('a-productions-close', 'date'),
        State('a-productions-festival', 'value'),
        prevent_initial_call=True
    )
    def new_production(n_clicks, name, venue, author, open, close, festival):
        return insert_production(name, venue, author, open, close, festival)


def register_productions_update_callbacks(app, server):
    @app.callback(
        Output('u-productions-role', 'data'),
        Input('u-productions-loaded', 'data'),
    )
    def update_role(loaded):
        return current_role(server)
    
    @app.callback(
        Output('u-productions-access', 'hidden'),
        Input('u-productions-role', 'data'),
    )
    def update_access_hidden(role):
        return role not in {"Committee", "Treasurer"}
    
    @app.callback(
        Output('u-productions-no-access', 'hidden'),
        Input('u-productions-role', 'data'),
    )
    def update_no_access_hidden(role):
        return role in {"Committee", "Treasurer"}

    @app.callback(
        Output('u-productions-select', 'options'),
        Input('u-productions-loaded', 'data'),
    )
    def update_productions(loaded):
        return get_productions()

    @app.callback(
        Output('u-productions-festival', 'options'),
        Input('u-productions-loaded', 'data'),
    )
    def update_festivals(loaded):
        return get_festivals()

    # @app.callback(
    #     Output('u-productions-position', 'options'),
    #     Input('u-productions-loaded', 'data'),
    # )
    # def update_names(loaded):
    #     return get_productions_positions()

    # @app.callback(
    #     Output('u-productions-message', 'children'),
    #     Input('u-productions-delete', 'n_clicks'),
    #     State('u-productions-position', 'value'),
    #     prevent_initial_call=True
    # )
    # def remove_productions_member(n_clicks, position):
    #     return delete_productions_member(position)
