import pandas as pd
from datetime import datetime

from current_role import current_role
from dash import Input, Output, State, ctx, dcc
from database import get_names
from members.database import get_member_check, get_member_list, insert_member
from variables import MEMBER_LIST_COLUMNS

def register_member_lookup_callbacks(app, server):
    @app.callback(
        Output('f-member-role', 'data'),
        Input('f-member-loaded', 'data'),
    )
    def update_role(loaded):
        return current_role(server)
    
    @app.callback(
        Output('f-member-no-access', 'hidden'),
        Input('f-member-role', 'data'),
    )
    def update_types_label(role):
        return role in {"Committee", "Treasurer"}
    
    @app.callback(
        Output('f-member-access', 'hidden'),
        Input('f-member-role', 'data'),
    )
    def update_types_label(role):
        return role not in {"Committee", "Treasurer"}
    
    @app.callback(
        Output('f-member-treasurer-access', 'hidden'),
        Input('f-member-role', 'data'),
    )
    def update_types_label(role):
        return role != "Treasurer"

    @app.callback(
        Output('f-member-columns', 'value'),
        Input('f-member-role', 'data'),
    )
    def update_columns_value(role):
        return [
                'Season', 'First Name', 'Surname'
            ] if role not in {"Committee", "Treasurer"} else [
                'Membership Type', 'First Name', 'Surname', 'Email'
            ]

    @app.callback(
        Output('f-member-persons', 'options'),
        Input('f-member-loaded', 'data'),
    )
    def update_names(loaded):
        return get_names()

    @app.callback(
        Output('f-member-list', 'columnDefs'),
        Input('f-member-columns', 'value'),
        Input('f-member-role', 'data'),
    )
    def update_column_defs(columns, role):
        return [
                {'field': 'season', 'headerName': 'Season'}, 
                {'field': 'first_name', 'headerName': 'First Name'}, 
                {'field': 'surname', 'headerName': 'Surname'},
            ] if role not in {"Committee", "Treasurer"} else [
                {'field': MEMBER_LIST_COLUMNS.get(col), 'headerName': col}
                for col in columns
            ]

    @app.callback(
        Output('f-member-list', 'rowData'),
        Input('f-member-role', 'data'),
        Input('f-member-seasons', 'value'),
        Input('f-member-types', 'value'),
        Input('f-member-persons', 'value'),
        Input('f-member-columns', 'value'),
    )
    def update_row_data(role, seasons, types, persons, columns):
        return get_member_list(role, seasons, types, persons, columns)

    @app.callback(
        Output('f-member-download', 'data'),
        Input('f-member-button', 'n_clicks'),
        State('f-member-list', 'rowData'),
        State('f-member-list', 'columnDefs'),
        prevent_initial_call=True
    )
    def export_member_data(n, members_list, columns):
        cols = [x['field'] for x in columns]
        df = pd.DataFrame(members_list)[cols]
        df.columns = [x['headerName'] for x in columns]
        df.index += 1
        today = datetime.now().strftime('%Y%m%d')
        writer = pd.ExcelWriter(f'vp_members_{today}.xlsx')
        df.to_excel(writer)
        writer.close()
        return dcc.send_file(f'vp_members_{today}.xlsx')


def register_member_search_callbacks(app):
    @app.callback(
        Output('s-member-message', 'children'),
        Input('s-member-search', 'n_clicks'),
        State('s-member-first-name', 'value'),
        State('s-member-surname', 'value'),
        State('s-member-email', 'value'),
        State('s-member-season', 'value'),
        prevent_initial_call=True
    )
    def check_member(n_clicks, first_name, surname, email, season):
        return get_member_check(first_name, surname, email, season)


def register_member_insert_callbacks(app, server):
    @app.callback(
        Output('a-member-role', 'data'),
        Input('a-member-loaded', 'data'),
    )
    def update_role(loaded):
        return current_role(server)
    
    @app.callback(
        Output('a-member-access', 'hidden'),
        Input('a-member-role', 'data'),
    )
    def update_access_hidden(role):
        return role != "Treasurer"
    
    @app.callback(
        Output('a-member-no-access', 'hidden'),
        Input('a-member-role', 'data'),
    )
    def update_no_access_hidden(role):
        return role == "Treasurer"

    @app.callback(
        Output('a-member-person', 'options'),
        Input('a-member-loaded', 'data'),
    )
    def update_names(loaded):
        return get_names()

    @app.callback(
        Output('a-member-message', 'children'),
        Input('a-member-insert', 'n_clicks'),
        Input('a-member-type', 'value'),
        Input('a-member-season', 'value'),
        Input('a-member-person', 'value'),
        prevent_initial_call=True
    )
    def new_member(n_clicks, m_type, season, person_id):
        if ctx.triggered_id == 'a-member-insert':
            return insert_member(m_type, season, person_id)
        return None
