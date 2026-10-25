from current_role import current_role
from dash import Input, Output, State, ctx, no_update
from database import get_festivals, get_productions, update_form_fill_in_value
from productions.database import (
    get_production_costs, get_production_details, insert_production,
    update_production, delete_production
)
from update_mapping import grey_out, update_mapping

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

    @app.callback(
        Output('f-productions-costs', 'rowData'),
        Input('f-productions-select', 'value'),
        State('f-productions-role', 'data')
    )
    def update_row_data_costs(production_id, role):
        if role in {'Committee', 'Treasurer'}:
            return get_production_costs(production_id)

        return []


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
        return get_festivals(add_empty=True)

    for field in ['venue', 'open', 'close']:
        @app.callback(
            Output(f'a-productions-{field}', 'disabled'),
            Input('a-productions-festival', 'value'),
        )
        def disable_production_field(festival):
            return bool(festival)

        @app.callback(
            Output(f'a-productions-{field}', 'style'),
            Input('a-productions-festival', 'value'),
        )
        def greyout_production_field(festival):
            return grey_out if bool(festival) else {}

        @app.callback(
            Output(f'a-productions-{field}', 'value' if field == 'venue' else 'date'),
            Input('a-productions-festival', 'value'),
        )
        def empty_production_field(festival):
            return None if bool(festival) else no_update

    for field in ['author', 'festival']:
        @app.callback(
            Output(f'a-productions-{field}', 'disabled'),
            Input('a-productions-type', 'value'),
        )
        def disable_festival_field(p_type):
            return p_type == 'Festival'

        @app.callback(
            Output(f'a-productions-{field}', 'style'),
            Input('a-productions-type', 'value'),
        )
        def greyout_festival_field(p_type):
            return grey_out if p_type == 'Festival' else {}

        @app.callback(
            Output(f'a-productions-{field}', 'value'),
            Input('a-productions-type', 'value'),
        )
        def empty_festival_field(p_type):
            return "" if p_type == 'Festival' else no_update

    @app.callback(
        Output('a-productions-message', 'children'),
        Input('a-productions-insert', 'n_clicks'),
        State('a-productions-type', 'value'),
        State('a-productions-name', 'value'),
        State('a-productions-venue', 'value'),
        State('a-productions-author', 'value'),
        State('a-productions-open', 'date'),
        State('a-productions-close', 'date'),
        State('a-productions-festival', 'value'),
        prevent_initial_call=True
    )
    def new_production(n_clicks, p_type, name, venue, author, open, close, festival):
        return insert_production(p_type, name, venue, author, open, close, festival)


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
        return get_festivals(add_empty=True)

    for datatype in ['value', 'date']:
        for field in update_mapping['productions'][datatype].keys():
            @app.callback(
                Output(f'u-productions-{field}', datatype),
                Input('u-productions-select', 'value'),
            )
            def update_field_value(selected_id, field=field):
                output =  update_form_fill_in_value('productions', field, selected_id)
                if not output:
                    output =  update_form_fill_in_value('festivals', field, selected_id)
                return output

    @app.callback(
        Output('u-productions-message', 'children'),
        Input('u-productions-update', 'n_clicks'),
        Input('u-productions-delete', 'n_clicks'),
        State('u-productions-select', 'value'),
        State('u-productions-venue', 'value'),
        State('u-productions-author', 'value'),
        State('u-productions-open', 'date'),
        State('u-productions-close', 'date'),
        State('u-productions-festival', 'value'),
        prevent_initial_call=True
    )
    def change_production_details(u_clicks, d_clicks, production_id, venue, author,
                              open_date, close_date, festival_id):
        if ctx.triggered_id == "u-productions-update":
            return update_production(production_id, venue, author,
                              open_date, close_date, festival_id)

        if ctx.triggered_id == "u-productions-delete":
            return delete_production(production_id)
