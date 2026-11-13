from dash import Input, Output, State

from balance.database import get_balance, insert_balance
from current_role import current_role


def register_balance_lookup_callbacks(app, server):
    @app.callback(
        Output('f-balance-role', 'data'),
        Input('f-balance-loaded', 'data'),
    )
    def update_role(loaded):
        return current_role(server)
    
    @app.callback(
        Output('f-balance-access', 'hidden'),
        Input('f-balance-role', 'data'),
    )
    def update_access_hidden(role):
        return role not in {"Committee", "Treasurer"}
    
    @app.callback(
        Output('f-balance-treasurer-access', 'hidden'),
        Input('f-balance-role', 'data'),
    )
    def update_treasurer_access_hidden(role):
        return role != "Treasurer"
    
    @app.callback(
        Output('f-balance-no-access', 'hidden'),
        Input('f-balance-role', 'data'),
    )
    def update_no_access_hidden(role):
        return role in {"Committee", "Treasurer"}

    @app.callback(
        Output('f-balance-list', 'rowData'),
        Input('f-balance-loaded', 'data'),
        Input('f-balance-month', 'value'),
        Input('f-balance-year', 'value'),
        Input('f-balance-start-date', 'date'),
        Input('f-balance-end-date', 'date'),
        State('f-balance-role', 'data')
    )
    def update_row_data_balance(loaded, month, year, start_date, end_date, role):
        if role in {'Committee', 'Treasurer'}:
            return get_balance(month, year, start_date, end_date)

        return []


def register_balance_insert_callbacks(app, server):
    @app.callback(
        Output('a-balance-role', 'data'),
        Input('a-balance-loaded', 'data'),
    )
    def update_role(loaded):
        return current_role(server)
    
    @app.callback(
        Output('a-balance-access', 'hidden'),
        Input('a-balance-role', 'data'),
    )
    def update_access_hidden(role):
        return role != "Treasurer"
    
    @app.callback(
        Output('a-balance-no-access', 'hidden'),
        Input('a-balance-role', 'data'),
    )
    def update_no_access_hidden(role):
        return role == "Treasurer"

    @app.callback(
        Output('a-balance-message', 'children'),
        Input('a-balance-insert', 'n_clicks'),
        State('a-balance-amount', 'value'),
        State('a-balance-month', 'value'),
        State('a-balance-year', 'value'),
        prevent_initial_call=True
    )
    def new_balance(n_clicks, amount, month, year):
        return insert_balance(amount, month, year)
