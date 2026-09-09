####

# dash_app/section_1/div_1.py

from dash import html


def layout():
    return html.Div(
        [
            html.H3("Section 1"),
            html.P("Content for this element."),
        ],
        id="section-1-div-1",
    )

####

# dash_app/section_1/layout.py

from dash import html

from . import div_1
from . import div_2
from . import div_3


def layout():
    return html.Div(
        [
            div_1.layout(),
            div_2.layout(),
            div_3.layout(),
        ],
        id="section-1",
    )

####

# dash_app/section_1/callbacks.py

from dash import Input, Output


def register_callbacks(app):

    @app.callback(
        Output("section-1-div-2-output", "children"),
        Input("section-1-div-1-button", "n_clicks"),
    )
    def update_div_2(n_clicks):
        if not n_clicks:
            return "Waiting..."
        return f"Clicked {n_clicks} times"

####

# dash_app/callbacks.py

from dash_app.section_1.callbacks import register_callbacks as register_section_1
from dash_app.section_2.callbacks import register_callbacks as register_section_2
from dash_app.section_3.callbacks import register_callbacks as register_section_3


def register_callbacks(app):

    register_section_1(app)
    register_section_2(app)
    register_section_3(app)

    # Callbacks involving multiple sections go here.

    @app.callback(...)
    def update_sections(...):
        ...

####

def build_layout(role):
    children = [
        section_1.layout(),
    ]

    if role in ("Member", "Admin"):
        children.append(section_2.layout())

    if role == "Admin":
        children.append(section_3.layout())

    return html.Div(children)
