from current_role import current_role
from dash import Input, Output, State, ctx
from database import get_names, get_productions


def register_transactions_insert_callbacks(app, server):
    @app.callback(
        Output('a-transactions-role', 'data'),
        Input('a-transactions-loaded', 'data'),
    )
    def update_role(loaded):
        return current_role(server)
    
    @app.callback(
        Output('a-transactions-access', 'hidden'),
        Input('a-transactions-role', 'data'),
    )
    def update_access_hidden(role):
        return role != "Treasurer"
    
    @app.callback(
        Output('a-transactions-no-access', 'hidden'),
        Input('a-transactions-role', 'data'),
    )
    def update_no_access_hidden(role):
        return role == "Treasurer"

    @app.callback(
        Output('a-transactions-recipient', 'options'),
        Input('a-transactions-loaded', 'data'),
    )
    def update_recipient(loaded):
        return get_names(add_empty=True)

    @app.callback(
        Output('a-transactions-renew', 'options'),
        Input('a-transactions-loaded', 'data'),
    )
    def update_renewing_member(loaded):
        return get_names()

    @app.callback(
        Output('a-transactions-existing', 'options'),
        Input('a-transactions-loaded', 'data'),
    )
    def update_existing_member(loaded):
        return get_names(add_empty=True)

    @app.callback(
        Output('a-transactions-production', 'options'),
        Input('a-transactions-loaded', 'data'),
    )
    def update_productions(loaded):
        return get_productions(add_empty=True)

    @app.callback(
        Output('a-transactions-message', 'children'),
        Input('a-transactions-insert', 'n_clicks'),
        State('a-transactions-type', 'value'),
        State('a-transactions-date', 'date'),
        State('a-transactions-amount', 'value'),
        State('a-transactions-description', 'value'),
        State('a-transactions-recipient', 'value'),
        State('a-transactions-recipient-text', 'value'),
        State('a-transactions-member-type', 'value'),
        State('a-transactions-renew', 'value'),
        State('a-transactions-new-1', 'value'),
        State('a-transactions-new-2', 'value'),
        State('a-transactions-new-3', 'value'),
        State('a-transactions-existing', 'value'),
        State('a-transactions-production', 'value'),
        prevent_initial_call=True
    )
    def new_transaction(n_clicks, t_type, date, amount, description, recipient, recipient_text,
                            m_type, renew, new_1, new_2, new_3, existing, production_id):
        return insert_transaction(t_type, date, amount, description, recipient, recipient_text,
                            m_type, renew, new_1, new_2, new_3, existing, production_id)


# def register_transactions_update_callbacks(app, server):
#     @app.callback(
#         Output('u-transactions-role', 'data'),
#         Input('u-transactions-loaded', 'data'),
#     )
#     def update_role(loaded):
#         return current_role(server)
    
#     @app.callback(
#         Output('u-transactions-access', 'hidden'),
#         Input('u-transactions-role', 'data'),
#     )
#     def update_access_hidden(role):
#         return role not in {"Committee", "Treasurer"}
    
#     @app.callback(
#         Output('u-transactions-no-access', 'hidden'),
#         Input('u-transactions-role', 'data'),
#     )
#     def update_no_access_hidden(role):
#         return role in {"Committee", "Treasurer"}

#     @app.callback(
#         Output('u-transactions-select', 'options'),
#         Input('u-transactions-loaded', 'data'),
#     )
#     def update_transactions_list(loaded):
#         return get_transactions()

#     for datatype in ['value', 'date']:
#         for field in update_mapping['transactions'][datatype].keys():
#             @app.callback(
#                 Output(f'u-transactions-{field}', datatype),
#                 Input('u-transactions-select', 'value'),
#             )
#             def update_field_value(selected_id, field=field):
#                 return update_form_fill_in_value('transactions', field, selected_id)

#     @app.callback(
#         Output('u-transactions-message', 'children'),
#         Input('u-transactions-update', 'n_clicks'),
#         Input('u-transactions-delete', 'n_clicks'),
#         State('u-transactions-select', 'value'),
#         State('u-transactions-role-name', 'value'),
#         prevent_initial_call=True
#     )
#     def change_transactions_details(u_clicks, d_clicks, role_id, name):
#         if ctx.triggered_id == "u-transactions-update":
#             return update_transactions(role_id, name)

#         if ctx.triggered_id == "u-transactions-delete":
#             return delete_transactions(role_id)
