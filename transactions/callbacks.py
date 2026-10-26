from datetime import date, timedelta

from current_role import current_role
from dash import Input, Output, State, no_update
from database import get_names, get_productions
from transactions.database import insert_transaction
from update_mapping import grey_out
from variables import BANK_COST, MEMBER_COST, STORAGE_COST, STORAGE_OWNER


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
        Output('a-transactions-date', 'date'),
        Input('a-transactions-loaded', 'data'),
        Input('a-transactions-type', 'value'),
    )
    def set_date(loaded, t_type):
        today = date.today()
        if t_type == 'Storage':
            return today.replace(day=1)
        if t_type == 'Bank Charges':
            return (today + timedelta(5)).replace(day=1) - timedelta(1)
        return today

    @app.callback(
        Output('a-transactions-amount', 'value'),
        Input('a-transactions-loaded', 'data'),
        Input('a-transactions-type', 'value'),
    )
    def set_amount(loaded, t_type):
        if t_type == 'Storage':
            return STORAGE_COST
        if t_type == 'Bank Charges':
            return BANK_COST
        if t_type == 'Membership Subscription':
            return MEMBER_COST
        return None

    @app.callback(
        Output('a-transactions-recipient', 'disabled'),
        Input('a-transactions-loaded', 'data'),
        Input('a-transactions-type', 'value'),
        Input('a-transactions-recipient-text', 'value'),
    )
    def disable_recipient(loaded, t_type, recipient):
        return not bool(t_type) or bool(recipient) or (t_type == 'Membership Subscription')

    @app.callback(
        Output('a-transactions-recipient', 'style'),
        Input('a-transactions-loaded', 'data'),
        Input('a-transactions-type', 'value'),
        Input('a-transactions-recipient-text', 'value'),
    )
    def greyout_recipient(loaded, t_type, recipient):
        return grey_out if (
            not bool(t_type) or bool(recipient) or (t_type == 'Membership Subscription')
        ) else {}

    @app.callback(
        Output('a-transactions-recipient', 'value'),
        Input('a-transactions-loaded', 'data'),
        Input('a-transactions-type', 'value'),
        Input('a-transactions-recipient-text', 'value'),
    )
    def empty_recipient(loaded, t_type, recipient):
        return None if (
            not bool(t_type) or bool(recipient) or (t_type == 'Membership Subscription')
        ) else no_update

    @app.callback(
        Output('a-transactions-recipient-text', 'disabled'),
        Input('a-transactions-loaded', 'data'),
        Input('a-transactions-type', 'value'),
        Input('a-transactions-recipient', 'value'),
    )
    def disable_recipient_text(loaded, t_type, recipient):
        return not bool(t_type) or bool(recipient) or (t_type == 'Membership Subscription')

    @app.callback(
        Output('a-transactions-recipient-text', 'style'),
        Input('a-transactions-loaded', 'data'),
        Input('a-transactions-type', 'value'),
        Input('a-transactions-recipient', 'value'),
    )
    def greyout_recipient_text(loaded, t_type, recipient):
        return grey_out if (
            not bool(t_type) or bool(recipient) or (t_type == 'Membership Subscription')
        ) else {}

    @app.callback(
        Output('a-transactions-recipient-text', 'value'),
        Input('a-transactions-loaded', 'data'),
        Input('a-transactions-type', 'value'),
        Input('a-transactions-recipient', 'value'),
    )
    def empty_recipient_text(loaded, t_type, recipient):
        if t_type == 'Storage':
            return STORAGE_OWNER
        return None if (
            not bool(t_type) or bool(recipient) or (t_type == 'Membership Subscription')
        ) else no_update

    @app.callback(
        Output('a-transactions-production', 'disabled'),
        Input('a-transactions-loaded', 'data'),
        Input('a-transactions-type', 'value'),
    )
    def disable_production(loaded, t_type):
        return not bool(t_type) or (t_type != 'Production')

    @app.callback(
        Output('a-transactions-production', 'style'),
        Input('a-transactions-loaded', 'data'),
        Input('a-transactions-type', 'value'),
    )
    def greyout_production(loaded, t_type):
        return grey_out if (
            not bool(t_type) or (t_type != 'Production')
        ) else {}

    @app.callback(
        Output('a-transactions-production', 'value'),
        Input('a-transactions-loaded', 'data'),
        Input('a-transactions-type', 'value'),
    )
    def empty_production(loaded, t_type):
        return None if (
            not bool(t_type) or (t_type != 'Production')
        ) else no_update

    for field in ['member-type', 'season', 'renew', 'new-1']:
        @app.callback(
            Output(f'a-transactions-{field}', 'disabled'),
            Input('a-transactions-loaded', 'data'),
            Input('a-transactions-type', 'value'),
            Input('a-transactions-existing', 'value'),
        )
        def disable_member_field(loaded, t_type, existing):
            return not bool(t_type) or bool(existing) or (t_type != 'Membership Subscription')

        @app.callback(
            Output(f'a-transactions-{field}', 'style'),
            Input('a-transactions-loaded', 'data'),
            Input('a-transactions-type', 'value'),
            Input('a-transactions-existing', 'value'),
        )
        def greyout_member_field(loaded, t_type, existing):
            return grey_out if (
                not bool(t_type) or bool(existing) or (t_type != 'Membership Subscription')
            ) else {}

        @app.callback(
            Output(f'a-transactions-{field}', 'value'),
            Input('a-transactions-loaded', 'data'),
            Input('a-transactions-type', 'value'),
            Input('a-transactions-existing', 'value'),
        )
        def empty_member_field(loaded, t_type, existing):
            return None if (
                not bool(t_type) or bool(existing) or (t_type != 'Membership Subscription')
            ) else no_update

    @app.callback(
        Output('a-transactions-new-2', 'disabled'),
        Input('a-transactions-loaded', 'data'),
        Input('a-transactions-new-1', 'value'),
    )
    def disable_new_2(loaded, new):
        return not bool(new)

    @app.callback(
        Output('a-transactions-new-2', 'style'),
        Input('a-transactions-loaded', 'data'),
        Input('a-transactions-new-1', 'value'),
    )
    def greyout_new_2(loaded, new):
        return grey_out if (
            not bool(new)
        ) else {}

    @app.callback(
        Output('a-transactions-new-2', 'value'),
        Input('a-transactions-loaded', 'data'),
        Input('a-transactions-new-1', 'value'),
    )
    def empty_new_2(loaded, new):
        return None if (
            not bool(new)
        ) else no_update

    @app.callback(
        Output('a-transactions-new-3', 'disabled'),
        Input('a-transactions-loaded', 'data'),
        Input('a-transactions-new-2', 'value'),
    )
    def disable_new_3(loaded, new):
        return not bool(new)

    @app.callback(
        Output('a-transactions-new-3', 'style'),
        Input('a-transactions-loaded', 'data'),
        Input('a-transactions-new-2', 'value'),
    )
    def greyout_new_3(loaded, new):
        return grey_out if (
            not bool(new)
        ) else {}

    @app.callback(
        Output('a-transactions-new-3', 'value'),
        Input('a-transactions-loaded', 'data'),
        Input('a-transactions-new-2', 'value'),
    )
    def empty_new_3(loaded, new):
        return None if (
            not bool(new)
        ) else no_update

    @app.callback(
        Output('a-transactions-existing', 'disabled'),
        Input('a-transactions-loaded', 'data'),
        Input('a-transactions-type', 'value'),
        Input('a-transactions-member-type', 'value'),
        Input('a-transactions-season', 'value'),
        Input('a-transactions-renew', 'value'),
        Input('a-transactions-new-1', 'value'),
    )
    def disable_existing(loaded, t_type, m_type, season, renew, new):
        return (
            not bool(t_type) or (t_type != 'Membership Subscription')
            or bool(m_type) or bool(season) or bool(renew) or bool(new)
        )

    @app.callback(
        Output('a-transactions-existing', 'style'),
        Input('a-transactions-loaded', 'data'),
        Input('a-transactions-type', 'value'),
        Input('a-transactions-member-type', 'value'),
        Input('a-transactions-season', 'value'),
        Input('a-transactions-renew', 'value'),
        Input('a-transactions-new-1', 'value'),
    )
    def greyout_existing(loaded, t_type, m_type, season, renew, new):
        return grey_out if (
            not bool(t_type) or (t_type != 'Membership Subscription')
            or bool(m_type) or bool(season) or bool(renew) or bool(new)
        ) else {}

    @app.callback(
        Output('a-transactions-existing', 'value'),
        Input('a-transactions-loaded', 'data'),
        Input('a-transactions-type', 'value'),
        Input('a-transactions-member-type', 'value'),
        Input('a-transactions-season', 'value'),
        Input('a-transactions-renew', 'value'),
        Input('a-transactions-new-1', 'value'),
    )
    def empty_existing(loaded, t_type, m_type, season, renew, new):
        return None if (
            not bool(t_type) or (t_type != 'Membership Subscription')
            or bool(m_type) or bool(season) or bool(renew) or bool(new)
        ) else no_update

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
        State('a-transactions-season', 'value'),
        State('a-transactions-renew', 'value'),
        State('a-transactions-new-1', 'value'),
        State('a-transactions-new-2', 'value'),
        State('a-transactions-new-3', 'value'),
        State('a-transactions-existing', 'value'),
        State('a-transactions-production', 'value'),
        prevent_initial_call=True
    )
    def new_transaction(n_clicks, t_type, date, amount, description, recipient, recipient_text,
                            m_type, season, renew, new_1, new_2, new_3, existing, production_id):
        return insert_transaction(t_type, date, amount, description, recipient, recipient_text,
                            m_type, season, renew, new_1, new_2, new_3, existing, production_id)


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
