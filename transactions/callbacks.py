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
    def update_people(loaded):
        return get_names()

    @app.callback(
        Output('a-transactions-renew', 'options'),
        Input('a-transactions-loaded', 'data'),
    )
    def update_people(loaded):
        return get_names()

    @app.callback(
        Output('a-transactions-existing', 'options'),
        Input('a-transactions-loaded', 'data'),
    )
    def update_people(loaded):
        return get_names()

    @app.callback(
        Output('a-transactions-production', 'options'),
        Input('a-transactions-loaded', 'data'),
    )
    def update_productions(loaded):
        return get_productions()

    # @app.callback(
    #     Output('a-transactions-message', 'children'),
    #     Input('a-transactions-insert', 'n_clicks'),
    #     State('a-transactions-type', 'value'),
    #     prevent_initial_call=True
    # )
    # def new_transactions(n_clicks, person_id, production_id, role, role_name):
    #     return insert_transactions(person_id, production_id, role, role_name)


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
