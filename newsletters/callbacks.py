from dash import Input, Output, State, ctx

from current_role import current_role
from newsletters.database import get_newsletters_list, insert_newsletter


def register_newsletters_lookup_callbacks(app, server):
    @app.callback(
        Output('f-newsletters-role', 'data'),
        Input('f-newsletters-loaded', 'data'),
    )
    def update_role(loaded):
        return current_role(server)
    
    @app.callback(
        Output('f-newsletters-access', 'hidden'),
        Input('f-newsletters-role', 'data'),
    )
    def update_access_hidden(role):
        return role not in {"Committee", "Treasurer"}

    @app.callback(
        Output('f-newsletters-select', 'options'),
        Input('f-newsletters-loaded', 'data'),
    )
    def update_newsletters_list(loaded):
        return get_newsletters_list()

    @app.callback(
        Output('f-newsletters-pdf', 'src'),
        Input('f-newsletters-select', 'value'),
    )
    def update_newsletter(url):
        return url


def register_newsletters_insert_callbacks(app, server):
    @app.callback(
        Output('a-newsletters-role', 'data'),
        Input('a-newsletters-loaded', 'data'),
    )
    def update_role(loaded):
        return current_role(server)
    
    @app.callback(
        Output('a-newsletters-access', 'hidden'),
        Input('a-newsletters-role', 'data'),
    )
    def update_access_hidden(role):
        return role not in {"Committee", "Treasurer"}
    
    @app.callback(
        Output('a-newsletters-no-access', 'hidden'),
        Input('a-newsletters-role', 'data'),
    )
    def update_no_access_hidden(role):
        return role in {"Committee", "Treasurer"}

    @app.callback(
        Output('a-newsletters-message', 'children'),
        Input('a-newsletters-insert', 'n_clicks'),
        Input('a-newsletters-sent', 'date'),
        Input('a-newsletters-url', 'value'),
        prevent_initial_call=True
    )
    def new_newsletter(n_clicks, sent_date, url):
        if ctx.triggered_id == "a-newsletters-insert":
            return insert_newsletter(sent_date, url)
        return None
