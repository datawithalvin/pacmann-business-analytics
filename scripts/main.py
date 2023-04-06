import numpy as np
import pandas as pd
import time

import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
from dash.dependencies import Input, Output

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY, "./style.css"])

choropleth_map_urls = {
    2015: "https://datawrapper.dwcdn.net/HDZHt/1/",
    2016: "https://datawrapper.dwcdn.net/6ezOJ/3/",
    2017: "https://datawrapper.dwcdn.net/5Lkpn/6/"
}



# load preprocessed data
filepath = "../datasets/preprocessed_data.csv"
main_df = pd.read_csv(filepath)



sidebar = dbc.Col(
    [
        html.H2("Dashboard Description"),
        html.P("Here you can write a brief description of the dashboard and its purpose."),
        html.H4("Filter by Year"),
        dcc.Dropdown(
            id="year_filter",
            options=[
                {"label": str(year), "value": year} for year in range(2015, 2018)
            ],
            value=2017,
            clearable=False,
            searchable=False,
        ),
    ],
    width={"size": 2, "order": 1, "offset": 0},
    className="h-100",
)

content = dbc.Col(
    [
        dbc.Row(
            [
                dbc.Col(html.Iframe(id="choropleth_map", src=choropleth_map_urls[2017], style={"width": "100%", "height": "53vh", "border": "none"}), width={"size": 7, "order": 1, "offset": 0}),
                dbc.Col(dcc.Graph(id="line_chart", figure={}, className="chart-container"), width={"size": 3, "order": 2, "offset": 0}),
            ],
        ),

        dbc.Row(
            [
                dbc.Col(dcc.Graph(id="scatter_plot", figure={}, className="chart-container"), width={"size": 3, "order": 1, "offset": 0}),
                dbc.Col(dcc.Graph(id="bar_chart", figure={}, className="chart-container"), width={"size": 4, "order": 2, "offset": 0}),
                dbc.Col(dcc.Graph(id="fill_rate_line_chart", figure={}, className="chart-container"), width={"size": 3, "order": 3, "offset": 0}),
            ],
        ),

        dbc.Row(
            [
                dbc.Col(dcc.Graph(id="otif_bar_chart", figure={}, className="chart-container"), width={"size": 3, "order": 1, "offset": 0}),
                dbc.Col(dcc.Graph(id="stacked_bar_chart", figure={}, className="chart-container"), width={"size": 4, "order": 2, "offset": 0}),
                dbc.Col(dcc.Graph(id="heatmap", figure={}, className="chart-container"), width={"size": 3, "order": 3, "offset": 0}),
            ],
        ),
    ],
    width={"size": 10, "order": 2, "offset": 0},
    className="h-100",
)

app.layout = dbc.Container(
    [
        dbc.Row(
            [
                sidebar,
                content
            ],
        )
    ],
    fluid=True,
    className="h-100",
)

@app.callback(
    Output("choropleth_map", "src"),
    Input("year_filter", "value")
)
def update_choropleth_map(year):
    return choropleth_map_urls.get(year, choropleth_map_urls[2017])

if __name__ == "__main__":
    app.run_server(debug=True)

