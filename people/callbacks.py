from current_role import current_role
from dash import Input, Output, State
from database import get_names_for_person_update


def register_people_insert_callbacks(app, server):
    @app.callback(
        Output('a-people-role', 'data'),
        Input('a-people-loaded', 'data'),
    )
    def update_role(loaded):
        return current_role(server)
    
    @app.callback(
        Output('a-people-access', 'hidden'),
        Input('a-people-role', 'data'),
    )
    def update_access_hidden(role):
        return role not in {"Committee", "Treasurer"}
    
    @app.callback(
        Output('a-people-no-access', 'hidden'),
        Input('a-people-role', 'data'),
    )
    def update_no_access_hidden(role):
        return role in {"Committee", "Treasurer"}


def register_people_update_callbacks(app, server):
    @app.callback(
        Output('u-people-role', 'data'),
        Input('u-people-loaded', 'data'),
    )
    def update_role(loaded):
        return current_role(server)
    
    @app.callback(
        Output('u-people-access', 'hidden'),
        Input('u-people-role', 'data'),
    )
    def update_access_hidden(role):
        return role not in {"Committee", "Treasurer"}
    
    @app.callback(
        Output('u-people-no-access', 'hidden'),
        Input('u-people-role', 'data'),
    )
    def update_no_access_hidden(role):
        return role in {"Committee", "Treasurer"}

    @app.callback(
        Output('u-people-select', 'options'),
        Input('u-people-loaded', 'data'),
    )
    def update_names(loaded):
        return get_names_for_person_update()
