import pandas as pd
from current_role import current_role
from datetime import datetime
from dash import Input, Output, State, dcc
from database import get_member_list, get_names
from variables import MEMBER_LIST_COLUMNS

def register_member_lookup_callbacks(app, server):
    @app.callback(
        Output('f-member-role', 'data'),
        Input('f-member-loaded', 'data'),
    )
    def update_role(loaded):
        return current_role(server)
    
    @app.callback(
        Output('f-member-access', 'hidden'),
        Input('f-member-role', 'data'),
    )
    def update_types_label(role):
        return role not in {"Committee", "Treasurer"}

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
