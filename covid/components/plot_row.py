import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html


def get_plot_row():
    return dbc.Row(
        [
            dbc.Col([dcc.Loading(dcc.Graph(id="map-plot-italy",))], lg=5,),
            dbc.Col(
                [
                    dcc.Loading(dcc.Graph(id="bar-plot-selected", figure={})),
                    dcc.Loading(dcc.Graph(id="bar-plot-overall", figure={})),
                ],
                lg=7,
            ),
        ],
    )
