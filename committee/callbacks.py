from dash import Input, Output, State, ctx

from committee.database import (
    delete_committee_member, get_committee_list, get_committee_positions,
    insert_committee_member, update_committee_member
)
from current_role import current_role
from database import get_names, update_form_fill_in_value
from update_mapping import update_mapping

def register_committee_lookup_callbacks(app, server):
    @app.callback(
        Output('f-committee-role', 'data'),
        Input('f-committee-loaded', 'data'),
    )
    def update_role(loaded):
        return current_role(server)
    
    @app.callback(
        Output('f-committee-access', 'hidden'),
        Input('f-committee-role', 'data'),
    )
    def update_access_hidden(role):
        return role not in {"Committee", "Treasurer"}

    @app.callback(
        Output('f-committee-list', 'rowData'),
        Input('f-committee-role', 'data'),
        Input('f-committee-seasons', 'value'),
    )
    def update_row_data(role, seasons):
        return get_committee_list(role, seasons)


def register_committee_insert_callbacks(app, server):
    @app.callback(
        Output('a-committee-role', 'data'),
        Input('a-committee-loaded', 'data'),
    )
    def update_role(loaded):
        return current_role(server)
    
    @app.callback(
        Output('a-committee-access', 'hidden'),
        Input('a-committee-role', 'data'),
    )
    def update_access_hidden(role):
        return role not in {"Committee", "Treasurer"}
    
    @app.callback(
        Output('a-committee-no-access', 'hidden'),
        Input('a-committee-role', 'data'),
    )
    def update_no_access_hidden(role):
        return role in {"Committee", "Treasurer"}

    @app.callback(
        Output('a-committee-person', 'options'),
        Input('a-committee-loaded', 'data'),
    )
    def update_names(loaded):
        return get_names()

    @app.callback(
        Output('a-committee-message', 'children'),
        Input('a-committee-insert', 'n_clicks'),
        State('a-committee-person', 'value'),
        State('a-committee-season', 'value'),
        State('a-committee-position', 'value'),
        State('a-committee-list-rank', 'value'),
        prevent_initial_call=True
    )
    def new_committee_member(n_clicks, person, season, position, list_rank):
        person_id = person.split('|')[0] if person else None
        return insert_committee_member(person_id, season, position, list_rank)


def register_committee_update_callbacks(app, server):
    @app.callback(
        Output('u-committee-role', 'data'),
        Input('u-committee-loaded', 'data'),
    )
    def update_role(loaded):
        return current_role(server)
    
    @app.callback(
        Output('u-committee-access', 'hidden'),
        Input('u-committee-role', 'data'),
    )
    def update_access_hidden(role):
        return role not in {"Committee", "Treasurer"}
    
    @app.callback(
        Output('u-committee-no-access', 'hidden'),
        Input('u-committee-role', 'data'),
    )
    def update_no_access_hidden(role):
        return role in {"Committee", "Treasurer"}

    @app.callback(
        Output('u-committee-position', 'options'),
        Input('u-committee-loaded', 'data'),
        Input('u-committee-season', 'value'),
    )
    def update_names(loaded, season):
        return get_committee_positions(season)

    for datatype in ['value', 'date']:
        for field in update_mapping['committee'][datatype].keys():
            @app.callback(
                Output(f'u-committee-{field}', datatype),
                Input('u-committee-position', 'value'),
            )
            def update_field_value(selected_id, field=field):
                return update_form_fill_in_value('committee', field, selected_id)

    @app.callback(
        Output('u-committee-message', 'children'),
        Input('u-committee-update', 'n_clicks'),
        Input('u-committee-delete', 'n_clicks'),
        State('u-committee-position', 'value'),
        State('u-committee-list-rank', 'value'),
        prevent_initial_call=True
    )
    def change_committee_member(u_clicks, d_clicks, position, list_rank):
        if ctx.triggered_id == "u-committee-update":
            return update_committee_member(position, list_rank)

        if ctx.triggered_id == "u-committee-delete":
            return delete_committee_member(position)
