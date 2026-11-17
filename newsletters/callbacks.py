from dash import Input, Output, State, ctx

from current_role import current_role
from database import update_form_fill_in_value
from newsletters.database import get_newsletters_list, insert_newsletter, update_newsletter
from update_mapping import update_mapping


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
    def get_newsletter(selected_id):
        return selected_id.split(' || ')[1] if bool(selected_id) else None


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
        Input('a-newsletters-name', 'value'),
        prevent_initial_call=True
    )
    def new_newsletter(n_clicks, sent_date, url, name):
        if ctx.triggered_id == "a-newsletters-insert":
            return insert_newsletter(sent_date, url, name)
        return None


def register_newsletters_update_callbacks(app, server):
    @app.callback(
        Output('u-newsletters-role', 'data'),
        Input('u-newsletters-loaded', 'data'),
    )
    def update_role(loaded):
        return current_role(server)
    
    @app.callback(
        Output('u-newsletters-access', 'hidden'),
        Input('u-newsletters-role', 'data'),
    )
    def update_access_hidden(role):
        return role not in {"Committee", "Treasurer"}
    
    @app.callback(
        Output('u-newsletters-no-access', 'hidden'),
        Input('u-newsletters-role', 'data'),
    )
    def update_no_access_hidden(role):
        return role in {"Committee", "Treasurer"}

    @app.callback(
        Output('u-newsletters-select', 'options'),
        Input('u-newsletters-loaded', 'data'),
    )
    def update_newsletters_list(loaded):
        return get_newsletters_list()

    for datatype in ['value', 'date']:
        for field in update_mapping['newsletters'][datatype].keys():
            @app.callback(
                Output(f'u-newsletters-{field}', datatype),
                Input('u-newsletters-select', 'value'),
            )
            def update_field_value(selected_id, field=field):
                newsletter_id = selected_id.split(' || ')[0] if selected_id else None
                return update_form_fill_in_value('newsletters', field, newsletter_id)

    @app.callback(
        Output('u-newsletters-message', 'children'),
        Input('u-newsletters-update', 'n_clicks'),
        Input('u-newsletters-select', 'value'),
        Input('u-newsletters-sent', 'date'),
        Input('u-newsletters-url', 'value'),
        Input('u-newsletters-name', 'value'),
        prevent_initial_call=True
    )
    def change_newsletter(n_clicks, newsletter_id, sent_date, url, name):
        if ctx.triggered_id == "u-newsletters-update":
            return update_newsletter(newsletter_id, sent_date, url, name)
        return None
