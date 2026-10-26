from dash import Input, Output, State

from balance.database import insert_balance
from current_role import current_role

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
