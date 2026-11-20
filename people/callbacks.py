from dash import Input, Output, ctx

from current_role import current_role
from database import get_names_for_person_update, update_form_fill_in_value
from people.database import delete_person, insert_person, update_person
from update_mapping import update_mapping


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

    @app.callback(
        Output('a-people-message', 'children'),
        Input('a-people-insert', 'n_clicks'),
        Input('a-people-first-name', 'value'),
        Input('a-people-surname', 'value'),
        Input('a-people-address', 'value'),
        Input('a-people-postcode', 'value'),
        Input('a-people-address-private', 'value'),
        Input('a-people-home-phone', 'value'),
        Input('a-people-home-phone-private', 'value'),
        Input('a-people-mobile', 'value'),
        Input('a-people-mobile-private', 'value'),
        Input('a-people-email', 'value'),
        Input('a-people-email-private', 'value'),
        Input('a-people-gender', 'value'),
        Input('a-people-gdpr', 'date'),
        Input('a-people-committee-email', 'value'),
        prevent_initial_call=True
    )
    def new_person(
        n_clicks, first_name, surname, address, postcode, address_private, home_phone,
        home_phone_private, mobile, mobile_private, email, email_private, gender,
        gdpr, committee_email
    ):
        if ctx.triggered_id == 'a-people-insert':
            return insert_person(first_name, surname, address, postcode, address_private,
                home_phone, home_phone_private, mobile, mobile_private, email, email_private,
                gender, gdpr, committee_email)
        return None


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

    for datatype in ['value', 'date']:
        for field in update_mapping['people'][datatype].keys():
            @app.callback(
                Output(f'u-people-{field}', datatype),
                Input('u-people-select', 'value'),
                Input('u-people-empty', 'n_clicks'),
            )
            def update_field_value(selected_id, empty_clicks, field=field):
                if ctx.triggered_id == 'u-people-empty':
                    return None
                return update_form_fill_in_value('people', field, selected_id)

    @app.callback(
        Output('u-people-message', 'children'),
        Input('u-people-update', 'n_clicks'),
        Input('u-people-delete', 'n_clicks'),
        Input('u-people-select', 'value'),
        Input('u-people-address', 'value'),
        Input('u-people-postcode', 'value'),
        Input('u-people-address-private', 'value'),
        Input('u-people-home-phone', 'value'),
        Input('u-people-home-phone-private', 'value'),
        Input('u-people-mobile', 'value'),
        Input('u-people-mobile-private', 'value'),
        Input('u-people-email', 'value'),
        Input('u-people-email-private', 'value'),
        Input('u-people-gender', 'value'),
        Input('u-people-gdpr', 'date'),
        Input('u-people-committee-email', 'value'),
        prevent_initial_call=True
    )
    def change_person_details(u_clicks, d_clicks, person_id, address, postcode,
            address_private, home_phone, home_phone_private, mobile, mobile_private,
            email, email_private, gender, gdpr, committee_email):
        if ctx.triggered_id == "u-people-update":
            return update_person(person_id, address, postcode, address_private, home_phone,
            home_phone_private, mobile, mobile_private, email, email_private, gender,
            gdpr, committee_email)

        if ctx.triggered_id == "u-people-delete":
            return delete_person(person_id)

        return None
