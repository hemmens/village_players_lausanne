import pandas as pd
from current_role import current_role
from datetime import datetime
from dash import Input, Output, State, dcc
from database import get_names
from flask import session

def register_committee_lookup_callbacks(app, server):
    @app.callback(
        Output('f-committee-role', 'data'),
        Input('f-committee-loaded', 'data'),
    )
    def update_role(loaded):
        return current_role(server)
    
    @app.callback(
        Output('f-committee-update', 'style'),
        Input('f-committee-role', 'data'),
    )
    def update_update_style(role):
        return {'display': 'none'} if role == "Public" else {}

    @app.callback(
        Output('f-committee-insert', 'style'),
        Input('f-committee-role', 'data'),
    )
    def update_insert_style(role):
        return {'display': 'none'} if role == "Public" else {}

    # @app.callback(
    #     Output('f-committee-list', 'rowData'),
    #     Input('f-committee-role', 'data'),
    #     Input('f-committee-seasons', 'value'),
    #     Input('f-committee-types', 'value'),
    #     Input('f-committee-persons', 'value'),
    #     Input('f-committee-columns', 'value'),
    # )
    # def update_row_data(role, seasons, types, persons, columns):
    #     return get_committee_list(role, seasons, types, persons, columns)

    # @app.callback(
    #     Output('f-committee-list', 'columnDefs'),
    #     Input('f-committee-columns', 'value'),
    # )
    # def update_column_defs(columns):
    #     return [
    #         {'field': COMMITTEE_LIST_COLUMNS.get(col), 'headerName': col}
    #         for col in columns
    #     ]
