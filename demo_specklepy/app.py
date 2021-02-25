# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import dash
import dash_core_components as dcc
import dash_html_components as html
from demo_specklepy.speckle_data import get_figures

external_stylesheets = [
    {
        "href": "https://fonts.googleapis.com/css2?"
        "family=Roboto:wght@400;700&display=swap"
        "family=Space+Mono:wght@400;700&display=swap",
        "rel": "stylesheet",
    },
]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "speckle-py demo"


figures = get_figures()

app.layout = html.Div(
    children=[
        html.Div(
            children=[
                html.H1(children="speckle-py example", className="header-title"),
                html.P(
                    children="""
                    Speckle is the open source data platform for AEC.
                    We free your data from proprietary file formats so you can own
                    and access your data wherever you need it - including Python!
                    """,
                    className="header-description",
                ),
            ],
            className="header",
        ),
        html.Div(
            children=[
                html.Div(
                    children=[
                        dcc.Graph(id="example-3d-scatter", figure=figures["vertices"])
                    ],
                    className="card",
                ),
                html.Div(
                    children=[
                        dcc.Graph(id="volume-pie-chart", figure=figures["volumes"])
                    ],
                    className="card",
                ),
                html.Div(
                    children=[
                        dcc.Graph(id="carbon-bar-graph", figure=figures["carbon bar"])
                    ],
                    className="card",
                ),
                html.Div(
                    children=[
                        dcc.Graph(id="carbon-pie-chart", figure=figures["carbon pie"])
                    ],
                    className="card",
                ),
            ],
            className="container",
        ),
    ],
)

if __name__ == "__main__":
    app.run_server(debug=True)
