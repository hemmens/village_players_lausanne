from dash import Input, Output, State, ctx

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
        State('a-people-first-name', 'value'),
        State('a-people-surname', 'value'),
        State('a-people-address', 'value'),
        State('a-people-postcode', 'value'),
        State('a-people-address-private', 'value'),
        State('a-people-home-phone', 'value'),
        State('a-people-home-phone-private', 'value'),
        State('a-people-mobile', 'value'),
        State('a-people-mobile-private', 'value'),
        State('a-people-email', 'value'),
        State('a-people-email-private', 'value'),
        State('a-people-gender', 'value'),
        State('a-people-gdpr', 'date'),
        State('a-people-committee-email', 'value'),
        prevent_initial_call=True
    )
    def new_person(
        n_clicks, first_name, surname, address, postcode, address_private, home_phone,
        home_phone_private, mobile, mobile_private, email, email_private, gender,
        gdpr, committee_email
    ):
        return insert_person(first_name, surname, address, postcode, address_private, home_phone,
        home_phone_private, mobile, mobile_private, email, email_private, gender,
        gdpr, committee_email)


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
            )
            def update_field_value(selected_id, field=field):
                return update_form_fill_in_value('people', field, selected_id)

    @app.callback(
        Output('u-people-message', 'children'),
        Input('u-people-update', 'n_clicks'),
        Input('u-people-delete', 'n_clicks'),
        State('u-people-select', 'value'),
        State('u-people-address', 'value'),
        State('u-people-postcode', 'value'),
        State('u-people-address-private', 'value'),
        State('u-people-home-phone', 'value'),
        State('u-people-home-phone-private', 'value'),
        State('u-people-mobile', 'value'),
        State('u-people-mobile-private', 'value'),
        State('u-people-email', 'value'),
        State('u-people-email-private', 'value'),
        State('u-people-gender', 'value'),
        State('u-people-gdpr', 'date'),
        State('u-people-committee-email', 'value'),
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
