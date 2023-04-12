import numpy as np
import pandas as pd
import time
import locale

import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
from dash.dependencies import Input, Output

import plotly.express as px
import plotly.graph_objs as go
from plotly.subplots import make_subplots

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY, "./style.css", "./dropdown.css"])

choropleth_map_urls = {
    2015: "https://datawrapper.dwcdn.net/HDZHt/1/",
    2016: "https://datawrapper.dwcdn.net/6ezOJ/3/",
    2017: "https://datawrapper.dwcdn.net/5Lkpn/6/"
}



# load preprocessed data
filepath = "../datasets/preprocessed_data_filtered_status.csv"
main_df = pd.read_csv(filepath)


unique_regions = sorted(main_df["order_region"].unique())
sorted_regions = ["All Regions"] + unique_regions

region_options = [{"label": region, "value": region} for region in sorted_regions]

sidebar = dbc.Col(
    [
        html.H3("DataCo Regional Performance Dashboard"),
        html.Hr(),
        html.P("Select Year:"),
        dcc.Dropdown(
            id="year_filter",
            options=[
                {"label": str(year), "value": year} for year in range(2015, 2018)
            ],
            value=2017,
            clearable=False,
            searchable=False,
        ),
        html.Hr(),
        html.P("Select Region:"),
        dcc.Dropdown(
            id="region_filter",
            options=region_options,
            value="All Regions",
            clearable=False,
            searchable=False,
        ),
        html.Hr(),
        html.P("Here you can write a brief description of the dashboard and its purpose."),
    ],
    width={"size": 2, "order": 1, "offset": 0},
    className="h-100",
)



content = dbc.Col(
    [
    
        dbc.Row(
            [
                dbc.Col(html.Div([html.H6(id="region_name"), html.H6(id="otif_rate")], style={"width": "100%", "border-style": "double", "text-align": "center"}), width={"size": 2, "order": 5, "offset": 0}),
                dbc.Col(html.Div([html.H6(id="avg_tittle"), html.H6(id="avg_days")], style={"width": "100%", "border-style": "double", "text-align": "center"}), width={"size": 2, "order": 4, "offset": 0}),
                dbc.Col(html.Div([html.H6(id="total_tittle"), html.H6(id="total_order")], style={"width": "100%", "border-style": "double", "text-align": "center"}), width={"size": 2, "order": 1, "offset": 0}),
                dbc.Col(html.Div([html.H6(id="sales_tittle"), html.H6(id="total_sales")], style={"width": "100%", "border-style": "double", "text-align": "center"}), width={"size": 2, "order": 2, "offset": 0}),
                dbc.Col(html.Div([html.H6(id="profit_tittle"), html.H6(id="total_profit")], style={"width": "100%", "border-style": "double", "text-align": "center"}), width={"size": 2, "order": 3, "offset": 0}),
            ],
        ),

        dbc.Row(
            [
                dbc.Col(html.Iframe(id="choropleth_map", src=choropleth_map_urls[2017], style={"width": "100%", "height": "40vh", "border": "none"}), width={"size": 5, "order": 2, "offset": 0}),
                dbc.Col([dbc.Row(dcc.Graph(id="productbar", figure={}, className="chart-container")),
                        dbc.Row(dcc.Graph(id="dailysales", figure={}, className="chart-container"))], width={"size": 5, "order": 1, "offset": 0}),
            ],
        ),

        dbc.Row(
            [
                dbc.Col(dcc.Graph(id="regionbar", figure={}, className="chart-container"), width={"size": 3, "order": 2, "offset": 0}),
                # dbc.Col(dcc.Graph(id="dailysales", figure={}, className="chart-container"), width={"size": 3, "order": 1, "offset": 0}),
                dbc.Col(dcc.Graph(id="relationship", figure={}, className="chart-container"), width={"size": 4, "order": 3, "offset": 0}),

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
    Output("regionbar", "figure"),
    Output("dailysales", "figure"),
    # Output("bottombarfig", "figure"),
    Output("productbar", "figure"),
    Output("otif_rate", "children"),
    Output("region_name", "children"),
    Output("avg_days", "children"),
    Output("avg_tittle", "children"),
    Output("total_tittle", "children"),
    Output("total_order", "children"),
    Output("sales_tittle", "children"),
    Output("total_sales", "children"),
    Output("profit_tittle", "children"),
    Output("total_profit", "children"),   
    Output("relationship", "figure"),   
    Input("year_filter", "value"),
    Input("region_filter", "value")
)
def update_dashboard(year, region):
    filtered_df = main_df[main_df["order_year"]==year]

    def create_placeholder_figures(filtered_df, region):
        # bottombarfig = create_bar_region2(filtered_df)
        regionbar = create_bar_region(filtered_df)
        dailysales = daily_sales(filtered_df, region)
        productbar = create_bar_region_combined(filtered_df, region)
        otif_rate = calculate_otif(filtered_df, region)
        region_name = "OTIF Rate"
        avg_days = calculate_avg_shipping(filtered_df, region)
        avg_tittle = "Average Delivered Days"
        total_tittle = "Total Order"
        total_order = calculate_total_order(filtered_df, region)
        sales_tittle = "Total Sales"
        total_sales = calculate_total_sales(filtered_df, region)
        profit_tittle = "Total Profit"
        total_profit = calculate_total_profit(filtered_df, region)
        relationship = get_shipping_relationship(filtered_df)


        return regionbar, dailysales, productbar, otif_rate, region_name, avg_days, avg_tittle, total_tittle, total_order, sales_tittle, total_sales, profit_tittle, total_profit, relationship
    
    def create_bar_region(dataframe):
        grouped = dataframe.groupby(["market", "order_region"]).agg(
            total_sales = ("sales", "sum")
        ).reset_index()

        grouped = grouped.sort_values(by="total_sales", ascending=False).reset_index()
        grouped["total_sales"] = round(grouped["total_sales"], 2)
        
        grouped = grouped.head(5)

        # format values in millions
        grouped['total_sales_formated'] = "$" + (grouped['total_sales'] / 1000000).round(2).astype(str) + 'M'

        # assign unique colors to each market
        color_map = {'LATAM': '#3366CC', 'Europe': '#DC3912', 'Pacific Asia': '#FF9900', 'USCA': '#109618', 'Africa': '#990099'}

        fig = px.bar(grouped, x="total_sales", y="order_region", orientation="h", text="total_sales_formated", color="market",
                        labels={"order_region":"", "total_sales":"Total Sales"}, template="plotly_dark",
                        color_discrete_map=color_map)

        fig.update_layout(yaxis={'categoryorder':'total ascending'})

        fig.update_layout(autosize=True,width=400,height=300)
        fig.update_layout(title="<b>Top 5 High-Performing Regions by Total Sales</b>",title_font_size=13)
        fig.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)','paper_bgcolor': 'rgba(0, 0, 0, 0)',})
        fig.update_xaxes(title_font=dict(size=12))
        fig.update_layout(xaxis_showgrid=False, yaxis_showgrid=False)
        fig.update_layout(legend_title_text='Market')
        

        return fig
    
    # def create_bar_region2(dataframe):
        grouped = dataframe.groupby(["market", "order_region"]).agg(
            total_sales = ("sales", "sum")
        ).reset_index()

        grouped = grouped.sort_values(by="total_sales", ascending=False).reset_index()
        grouped["total_sales"] = round(grouped["total_sales"], 2)

        grouped = grouped.tail(5)

        # format values in millions
        grouped['total_sales_formated'] = "$" + (grouped['total_sales'] / 1000).round(2).astype(str) + 'K'

        # assign unique colors to each market
        color_map = {'LATAM': '#3366CC', 'Europe': '#DC3912', 'Pacific Asia': '#FF9900', 'USCA': '#109618', 'Africa': '#990099'}

        fig = px.bar(grouped, x="total_sales", y="order_region", orientation="h", text="total_sales_formated", color="market",
                        labels={"order_region":"", "total_sales":"Total Sales"}, template="plotly_dark",
                        color_discrete_map=color_map)

        fig.update_layout(yaxis={'categoryorder':'total ascending'})

        fig.update_layout(autosize=True,width=400,height=300)
        fig.update_layout(title="<b>Bottom 5 Underperforming Regions by Total Sales</b>",title_font_size=13)
        fig.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)','paper_bgcolor': 'rgba(0, 0, 0, 0)',})
        fig.update_xaxes(title_font=dict(size=12))
        fig.update_layout(xaxis_showgrid=False, yaxis_showgrid=False)
        fig.update_layout(legend_title_text='Market')
        

        return fig
    
    # def create_bar_region_market_combined(dataframe):

    #     grouped = dataframe.groupby(["market", "order_region"]).agg(
    #         total_sales = ("sales", "sum")
    #     ).reset_index()

    #     grouped["total_sales"] = round(grouped["total_sales"], 2)

    #     # sort by total_sales and split into two groups
    #     grouped = grouped.sort_values(by="total_sales", ascending=False).reset_index()

    #     # format total_sales as a string with $ and thousand separator
    #     locale.setlocale(locale.LC_ALL, '')  # set locale to default system locale
    #     grouped["total_sales_formated"] = grouped["total_sales"].apply(lambda x: locale.currency(x, grouping=True))

    #     top_5 = grouped.head(5)
    #     bottom_5 = grouped.tail(5)

    #     # assign unique colors to each market
    #     color_map = {'LATAM': '#3366CC', 'Europe': '#DC3912', 'Pacific Asia': '#FF9900', 'USCA': '#109618', 'Africa': '#990099'}

    #     # map category colors to the top_5 and bottom_5 dataframes
    #     top_5['color'] = top_5['market'].map(color_map)
    #     bottom_5['color'] = bottom_5['market'].map(color_map)

    #     # create the subplots
    #     fig = make_subplots(rows=2, cols=1, vertical_spacing=0.2, subplot_titles=(
    #         "<b>Top 5 High-Performing Regions by Total Sales</b>", 
    #         "<b>Bottom 5 Underperforming Regions by Total Sales</b>"))

    #     # add the top 5 subplot
    #     fig.add_trace(go.Bar(x=top_5['total_sales'], y=top_5['order_region'], orientation='h',
    #                         text=top_5['total_sales_formated'], name='', marker=dict(color=top_5['color']),
    #                         textfont=dict(color='white')),
    #                 row=1, col=1)
    #     fig.update_yaxes(title='', categoryorder='total ascending', row=1, col=1)
    #     fig.update_xaxes(title='Total Sales', row=1, col=1, showgrid=False)

    #     # add the bottom 5 subplot
    #     fig.add_trace(go.Bar(x=bottom_5['total_sales'], y=bottom_5['order_region'], orientation='h',
    #                         text=bottom_5['total_sales_formated'], name='', marker=dict(color=bottom_5['color']),
    #                         textfont=dict(color='white')),
    #                 row=2, col=1)
    #     fig.update_yaxes(title='', categoryorder='total ascending', row=2, col=1)
    #     fig.update_xaxes(title='Total Sales', row=2, col=1, showgrid=False)

    #     # update the layout
    #     fig.update_layout(
    #         height=400,
    #         width=500,
    #         template="plotly_dark",
    #         showlegend=True,
    #         margin=dict(l=0, r=0, t=20, b=0),
    #     )
    #     fig.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)','paper_bgcolor': 'rgba(0, 0, 0, 0)',})
    #     fig.update_annotations(font_size=12)

    #     return fig

    
    def create_bar_region_combined(dataframe, region):
        if region == "All Regions":
            grouped = dataframe.groupby(["category_name"]).agg(total_sales=("sales", "sum")).reset_index()
        else:
            dataframe = dataframe[dataframe["order_region"]==region]
            grouped = dataframe.groupby(["category_name"]).agg(total_sales=("sales", "sum")).reset_index()

        grouped["total_sales"] = round(grouped["total_sales"], 2)

        # sort by total_sales and split into two groups
        grouped = grouped.sort_values(by="total_sales", ascending=False).reset_index()

        # format total_sales as a string with $ and thousand separator
        locale.setlocale(locale.LC_ALL, '')  # set locale to default system locale
        grouped["total_sales_formated"] = grouped["total_sales"].apply(lambda x: locale.currency(x, grouping=True))

        top_5 = grouped.head(5)
        bottom_5 = grouped.tail(5)

        # create a dictionary to map each category to a unique color
        category_colors = {
            'Camping & Hiking': '#1f77b4',
            'Water Sports': '#ff7f0e',
            "Women's Apparel": '#2ca02c',
            "Men's Footwear": '#d62728',
            'Indoor/Outdoor Games': '#9467bd',
            'Accessories': '#8c564b',
            'Cleats': '#e377c2',
            'Trade-In': '#7f7f7f',
            'Cardio Equipment': '#bcbd22',
            'Shop By Sport': '#17becf',
            'Hockey': '#ff5733',
            'Electronics': '#e74c3c',
            'Fishing': '#3498db',
            'Golf Balls': '#9b59b6',
            'Lacrosse': '#e67e22',
            'Baseball & Softball': '#34495e',
            'Golf Gloves': '#f1c40f',
            "Girls' Apparel": '#2ecc71',
            'Fitness Accessories': '#1abc9c',
            'Hunting & Shooting': '#95a5a6',
            'Tennis & Racquet': '#2c3e50',
            'Golf Shoes': '#bdc3c7',
            'Golf Apparel': '#d35400',
            'Boxing & MMA': '#7f8c8d',
            "Men's Golf Clubs": '#2980b9',
            "Kids' Golf Clubs": '#16a085',
            'Soccer': '#c0392b',
            "Women's Golf Clubs": '#f39c12',
            'Golf Bags & Carts': '#27ae60',
            'Strength Training': '#e67e22',
            'As Seen on  TV!': '#8e44ad',
            'Basketball': '#f39c12',
            'Books ': '#1abc9c',
            'Baby ': '#95a5a6',
            'CDs ': '#d35400',
            'Cameras ': '#bdc3c7',
            "Children's Clothing": '#9b59b6',
            'Computers': '#7f8c8d',
            'Consumer Electronics': '#2c3e50',
            'Crafts': '#27ae60',
            'DVDs': '#f1c40f',
            'Garden': '#17becf',
            'Health and Beauty': '#bcbd22',
            "Men's Clothing": '#e74c3c',
            'Music': '#8c564b',
            'Pet Supplies': '#2ecc71',
            'Sporting Goods': '#7f7f7f',
            'Toys': '#d62728',
            'Video Games': '#9467bd',
            "Women's Clothing": '#3498db'
        }

        # map category colors to the top_5 and bottom_5 dataframes
        top_5['color'] = top_5['category_name'].map(category_colors)
        bottom_5['color'] = bottom_5['category_name'].map(category_colors)

        # create the subplots
        fig = make_subplots(rows=2, cols=1, vertical_spacing=0.2, subplot_titles=(
            f"<b>Top 5 High-Performing Categories in {region}</b>", 
            f"<b>Bottom 5 Underperforming Categories in {region}</b>"))

        # add the top 5 subplot
        fig.add_trace(go.Bar(x=top_5['total_sales'], y=top_5['category_name'], orientation='h',
                            text=top_5['total_sales_formated'], name='', marker=dict(color=top_5['color']),
                            textfont=dict(color='white')),
                    row=1, col=1)
        fig.update_yaxes(title='', categoryorder='total ascending', row=1, col=1)
        fig.update_xaxes(title='Total Sales', row=1, col=1, showgrid=False)

        # add the bottom 5 subplot
        fig.add_trace(go.Bar(x=bottom_5['total_sales'], y=bottom_5['category_name'], orientation='h',
                            text=bottom_5['total_sales_formated'], name='', marker=dict(color=bottom_5['color']),
                            textfont=dict(color='white')),
                    row=2, col=1)
        fig.update_yaxes(title='', categoryorder='total ascending', row=2, col=1)
        fig.update_xaxes(title='Total Sales', row=2, col=1, showgrid=False)

        # update the layout
        fig.update_layout(
            height=400,
            width=500,
            template="plotly_dark",
            showlegend=False,
            margin=dict(l=0, r=0, t=20, b=0),
        )
        fig.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)','paper_bgcolor': 'rgba(0, 0, 0, 0)',})
        fig.update_annotations(font_size=12)

        return fig

    def calculate_otif(dataframe, region):
        dataframe['on_time_in_full'] = (dataframe['shipping_days_difference'] >= 0).astype(int)
        # Group the data by 'order_region' and calculate the total number of orders and the total number of on-time, in-full orders.
        region_otif_data = dataframe.groupby('order_region')['on_time_in_full'].agg(['sum', 'count']).reset_index()

        # Calculate the OTIF rate for each region by dividing the total number of on-time, in-full orders by the total number of orders, then multiply by 100 to get the percentage.
        region_otif_data['otif_rate'] = (region_otif_data['sum'] / region_otif_data['count']) * 100

        # Rename the columns for better readability
        region_otif_data.columns = ['order_region', 'on_time_in_full_orders', 'total_orders', 'otif_rate']
        all_otif = (region_otif_data['on_time_in_full_orders'].sum() / region_otif_data['total_orders'].sum()) * 100
        region_otif_data.loc[len(region_otif_data)] = ['All Regions', region_otif_data['on_time_in_full_orders'].sum(),  
                                                       region_otif_data['total_orders'].sum(), all_otif]        

        value = str(round(region_otif_data[region_otif_data["order_region"]==region]["otif_rate"].values[0], 2)) + " %"

        return value
    
    def calculate_avg_shipping(dataframe, region):

        avg_scheduled_shipping_time = dataframe.groupby(['order_region'])['days_for_shipping_real'].mean().reset_index()
        avg_scheduled_shipping_time.loc[len(avg_scheduled_shipping_time)] = ['All Regions', avg_scheduled_shipping_time['days_for_shipping_real'].mean()]
        avg_scheduled_shipping_time = str(round(avg_scheduled_shipping_time[avg_scheduled_shipping_time["order_region"]==region]["days_for_shipping_real"].values[0], 2)) + " days"

        return avg_scheduled_shipping_time
    
    def calculate_total_order(dataframe, region):

        total_order = dataframe.groupby(['order_region'])['order_item_quantity'].sum().reset_index()
        total_order.loc[len(total_order)] = ['All Regions', total_order['order_item_quantity'].sum()]
        order_value = total_order[total_order["order_region"]==region]["order_item_quantity"].values[0]
        formatted_order = "{:,.0f}".format(order_value)
        total_order = formatted_order

        return total_order
    
    def calculate_total_sales(dataframe, region):

        total_sales = dataframe.groupby(['order_region'])['sales'].sum().reset_index()
        total_sales.loc[len(total_sales)] = ['All Regions', total_sales['sales'].sum()]
        sales_value = total_sales[total_sales["order_region"]==region]["sales"].values[0]
        formatted_sales = "${:,.2f}".format(sales_value)
        total_sales = formatted_sales

        return total_sales
    
    def calculate_total_profit(dataframe, region):

        total_profit = dataframe.groupby(['order_region'])['order_profit_per_order'].sum().reset_index()
        total_profit.loc[len(total_profit)] = ['All Regions', total_profit['order_profit_per_order'].sum()]
        profit_value = total_profit[total_profit["order_region"]==region]["order_profit_per_order"].values[0]
        formatted_profit = "${:,.2f}".format(profit_value)
        profit = formatted_profit

        return profit

    def daily_sales(dataframe, region):
        dataframe['order_date'] = pd.to_datetime(dataframe['order_date'])
        dataframe = dataframe.set_index('order_date')

        if region != "All Regions":
            dataframe = dataframe[dataframe["order_region"] == region]

        daily_sales = dataframe.resample('D')['sales'].sum().reset_index()

        daily_sales["sales"] = round(daily_sales["sales"], 2)
        daily_sales["order_date"] = daily_sales["order_date"].dt.strftime("%Y-%m-%d")

        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=daily_sales["order_date"],
                y=daily_sales["sales"],
                mode="lines",
                hovertemplate='<b>Date:</b> %{x}<br><b>Sales:</b> $%{y:,.2f}<extra></extra>',
            )
        )

        fig.update_layout(
            title=f"<b>{region} Sales Over Time</b>",
            xaxis_title="",
            yaxis_title="Sales",
            width=450,
            height=300,
            template="plotly_dark",
            title_font_size=13
        )

        fig.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)','paper_bgcolor': 'rgba(0, 0, 0, 0)',})

        return fig

    def get_shipping_relationship(dataframe):
            # Calculate the average days for shipping (actual vs. scheduled) and average sales by region
            avg_days_sales = dataframe.groupby('order_region').agg({'days_for_shipping_real': 'mean',
                                                            'days_for_shipment_scheduled': 'mean',
                                                            'sales': 'mean'}).reset_index()

            # Create the scatter plot using Plotly
            fig = px.scatter(avg_days_sales, x='days_for_shipping_real', y='days_for_shipment_scheduled',
                            size='sales', color='order_region', hover_name='order_region',
                            labels={'days_for_shipping_real': 'Average Days for Shipping (Actual)',
                                    'days_for_shipment_scheduled': 'Average Days for Shipping (Scheduled)',
                                    'sales': 'Average Sales'})

            # Customize the chart appearance
            fig.update_layout(title={'text': 'Relationship between Average Days for Shipping (Actual vs. Scheduled)<br>and<br>Average Sales by Region</br>',
                                    'font': {'size': 13},
                                    'x': 0.5,
                                    'xanchor': 'center'},
                            height=300,
                            width=500,
                            template="plotly_dark",
                            showlegend=True,
                            margin=dict(l=0, r=0, t=80, b=0),
                            plot_bgcolor='rgba(0, 0, 0, 0)',
                            paper_bgcolor='rgba(0, 0, 0, 0)')

            fig.update_xaxes(title_font=dict(size=11))
            fig.update_yaxes(title_font=dict(size=11))

            fig.update_traces(hovertemplate='<b>%{hovertext}</b><br>Average Days for Shipping (Actual): %{x:.2f}<br>Average Days for Shipping (Scheduled): %{y:.2f}<br>Average Sales: $%{marker.size:.2f}')

            fig.update_layout(legend_title_text='Region', legend=dict(font=dict(size=11)))

            # Display the chart
            return fig


    regionbar, dailysales, productbar, otif_rate, region_name, avg_days, avg_tittle, total_tittle, total_order, sales_tittle,  total_sales, profit_tittle, total_profit, relationship = create_placeholder_figures(filtered_df, region)


    return choropleth_map_urls.get(year), regionbar, dailysales, productbar, otif_rate, region_name, avg_days, avg_tittle, total_tittle, total_order, sales_tittle,  total_sales, profit_tittle, total_profit, relationship



if __name__ == "__main__":
    app.run_server(debug=True)

