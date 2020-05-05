import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash import Dash
from dash.dependencies import Input, Output, State

from ..components.control_row import get_control_row
from ..components.plot_row import get_plot_row
from ..components.world import get_world_layout


def set_callbacks_page(app: Dash):
    @app.callback(
        [Output(f"navlink-italy", "active"), Output("navlink-world", "active"),],
        [Input("url", "pathname")],
    )
    def toggle_active_links(pathname):
        if pathname == "/":
            # Treat page 1 as the homepage / index
            return False, False
        return [pathname == "/italy", pathname == "/world"]

    @app.callback(
        Output("container", "children"), [Input("url", "pathname")],
    )
    def update_dropdown_menu(pathname: str):
        if pathname == "/italy":
            return [get_control_row(), get_plot_row()]
        elif pathname == "/world":
            return get_world_layout()
        else:
            return [get_control_row(), get_plot_row()]
