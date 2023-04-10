import numpy as np
import pandas as pd
import time

import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
from dash.dependencies import Input, Output

import plotly.express as px
import plotly.graph_objects as go

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
                dbc.Col(dcc.Graph(id="barfig1", figure={}, className="chart-container"), width={"size": 3, "order": 2, "offset": 0}),
            ],
        ),

        dbc.Row(
            [
                dbc.Col(dcc.Graph(id="barfig2", figure={}, className="chart-container"), style={"height": "40vh", "border": "none"}, width={"size": 3, "order": 1, "offset": 0}),
                dbc.Col(dcc.Graph(id="barfig3", figure={}, className="chart-container"), width={"size": 4, "order": 2, "offset": 0}),
                dbc.Col(dcc.Graph(id="fill_rate_line_chart", figure={}, className="chart-container"), width={"size": 3, "order": 3, "offset": 0}),
            ],
        ),

        # dbc.Row(
        #     [
        #         dbc.Col(dcc.Graph(id="otif_bar_chart", figure={}, className="chart-container"), width={"size": 3, "order": 1, "offset": 0}),
        #         dbc.Col(dcc.Graph(id="stacked_bar_chart", figure={}, className="chart-container"), width={"size": 4, "order": 2, "offset": 0}),
        #         dbc.Col(dcc.Graph(id="heatmap", figure={}, className="chart-container"), width={"size": 3, "order": 3, "offset": 0}),
        #     ],
        # ),
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
    Output("barfig1", "figure"),
    Input("year_filter", "value")
)
def update_choropleth_map(year):
    filtered_df = main_df[main_df["order_year"]==year]

    def create_placeholder_figures(filtered_df):
        barfig1 = create_bar_region(filtered_df)

        return barfig1
    
    def create_bar_region(dataframe):
        grouped = dataframe.groupby(["market", "order_region"]).agg(
            total_sales = ("sales", "sum")
        ).reset_index()

        grouped = grouped.sort_values(by="total_sales", ascending=False).reset_index()
        grouped["total_sales"] = round(grouped["total_sales"], 2)
        grouped = grouped.head(10)

        # format values in millions
        grouped['total_sales_formatted'] = (grouped['total_sales'] / 1000000).round(2).astype(str) + 'M'

        fig = px.bar(grouped, x="total_sales", y="order_region", orientation="h", text="total_sales_formatted", color="market",
                        labels={"order_region":"", "total_sales":"Total Sales"}, template="plotly_dark",
                        color_discrete_sequence=px.colors.qualitative.Safe)

        fig.update_layout(yaxis={'categoryorder':'total ascending'})

        fig.update_layout(autosize=True,width=600,height=500)
        fig.update_layout(title="<b>Top 10 Total Sales Across Different Regions and Markets</b>",title_font_size=14)
        fig.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)','paper_bgcolor': 'rgba(0, 0, 0, 0)',})
        fig.update_xaxes(title_font=dict(size=12))
        fig.update_layout(xaxis_showgrid=False, yaxis_showgrid=False)
        

        return fig

    barfig1 = create_placeholder_figures(filtered_df)

    return choropleth_map_urls.get(year), barfig1



if __name__ == "__main__":
    app.run_server(debug=True)

