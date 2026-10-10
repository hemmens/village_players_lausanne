from current_role import current_role
from dash import Input, Output, State, ctx
from database import (
    get_names, get_castcrew, get_productions, update_form_fill_in_value, insert_castcrew,
    update_castcrew, delete_castcrew
)
from update_mapping import update_mapping


def register_castcrew_insert_callbacks(app, server):
    @app.callback(
        Output('a-castcrew-role', 'data'),
        Input('a-castcrew-loaded', 'data'),
    )
    def update_role(loaded):
        return current_role(server)
    
    @app.callback(
        Output('a-castcrew-access', 'hidden'),
        Input('a-castcrew-role', 'data'),
    )
    def update_access_hidden(role):
        return role not in {"Committee", "Treasurer"}
    
    @app.callback(
        Output('a-castcrew-no-access', 'hidden'),
        Input('a-castcrew-role', 'data'),
    )
    def update_no_access_hidden(role):
        return role in {"Committee", "Treasurer"}

    @app.callback(
        Output('a-castcrew-person', 'options'),
        Input('a-castcrew-loaded', 'data'),
    )
    def update_people(loaded):
        return get_names()

    @app.callback(
        Output('a-castcrew-production', 'options'),
        Input('a-castcrew-loaded', 'data'),
    )
    def update_productions(loaded):
        return get_productions()

    @app.callback(
        Output('a-castcrew-message', 'children'),
        Input('a-castcrew-insert', 'n_clicks'),
        State('a-castcrew-person', 'value'),
        State('a-castcrew-production', 'value'),
        State('a-castcrew-position', 'value'),
        State('a-castcrew-role-name', 'value'),
        prevent_initial_call=True
    )
    def new_castcrew(n_clicks, person_id, production_id, role, role_name):
        return insert_castcrew(person_id, production_id, role, role_name)


def register_castcrew_update_callbacks(app, server):
    @app.callback(
        Output('u-castcrew-role', 'data'),
        Input('u-castcrew-loaded', 'data'),
    )
    def update_role(loaded):
        return current_role(server)
    
    @app.callback(
        Output('u-castcrew-access', 'hidden'),
        Input('u-castcrew-role', 'data'),
    )
    def update_access_hidden(role):
        return role not in {"Committee", "Treasurer"}
    
    @app.callback(
        Output('u-castcrew-no-access', 'hidden'),
        Input('u-castcrew-role', 'data'),
    )
    def update_no_access_hidden(role):
        return role in {"Committee", "Treasurer"}

    @app.callback(
        Output('u-castcrew-select', 'options'),
        Input('u-castcrew-loaded', 'data'),
    )
    def update_castcrew_list(loaded):
        return get_castcrew()

    for datatype in ['value', 'date']:
        for field in update_mapping['castcrew'][datatype].keys():
            @app.callback(
                Output(f'u-castcrew-{field}', datatype),
                Input('u-castcrew-select', 'value'),
            )
            def update_field_value(selected_id, field=field):
                return update_form_fill_in_value('castcrew', field, selected_id)

    @app.callback(
        Output('u-castcrew-message', 'children'),
        Input('u-castcrew-update', 'n_clicks'),
        Input('u-castcrew-delete', 'n_clicks'),
        State('u-castcrew-select', 'value'),
        State('u-castcrew-role-name', 'value'),
        prevent_initial_call=True
    )
    def change_castcrew_details(u_clicks, d_clicks, role_id, name):
        if ctx.triggered_id == "u-castcrew-update":
            return update_castcrew(role_id, name)

        if ctx.triggered_id == "u-castcrew-delete":
            return delete_castcrew(role_id)
