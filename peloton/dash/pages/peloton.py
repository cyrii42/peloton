import dash_bootstrap_components as dbc
import plotly.express as px
from dash import Input, Output, callback, dash_table, dcc, html, register_page

import peloton.dash.utils.functions as dash_funcs
import peloton.helpers as helpers
import peloton.peloton_pivots as pivots

register_page(
    __name__,
    title='Peloton Data - Dash'
)

mariadb_engine = helpers.create_mariadb_engine(database="peloton")

df_table = dash_funcs.create_table_df(mariadb_engine)

sql_data_for_pivots = pivots.get_sql_data_for_pivots(mariadb_engine)

df_pivot_month = pivots.get_pivot_table_month(sql_data_for_pivots, ascending=False)

df_pivot_year = pivots.get_pivot_table_year(sql_data_for_pivots, ascending=False)

# Define list of columns for datatable
table_column_list = [
    'start_time_iso',
    'start_time',
    'instructor',
    'title',
    'min',
    'calories',
    'output',
    'output/min',
]

# Define lists of columns for charts
yaxis_radio_buttons = [
    'calories',
    'output',
    'output/min',
    'strive_score'
    ]

xaxis_radio_buttons = [
    'month',
    'start_time_iso',
    'instructor',
    ]

metric_radio_buttons = [
    'avg',
    'sum',
    'max',
    'min',
    'count'
]

chart_radio_buttons = [
    'histogram',
    'pie',
]

layout = html.Div([
    dbc.Row([
        html.Div("Zach's Peloton Data", className="text-primary text-center fs-3")
    ]),    
    dbc.Row([
        dbc.Col([
            html.Div('Latest Rides', className="text-primary text-center fs-4")
        ]),
        dbc.Col([
            html.Div('Pivot Tables', className="text-primary text-center fs-4")
        ]),
    ]),
    dbc.Row([
        dbc.Col([
            dash_table.DataTable(
                data=df_table[table_column_list].sort_values(by='start_time_iso', ascending=False).drop(columns=['start_time_iso']).to_dict('records'),
                page_size=15, 
                # sort_action='native',
                # filter_action='native',
                style_table={
                    'overflowX': 'auto'
                    }, 
                style_header={
                    'fontSize': 16,
                    'font-family':'system-ui',
                    'backgroundColor': 'rgb(80, 80, 80)',
                    'color': 'white',
                    'textAlign': 'center'
                    },
                style_data={
                    'fontSize': 16,
                    'font-family':'system-ui',
                    'backgroundColor': 'rgb(50, 50, 50)',
                    'color': 'white'
                    },
            )
        ]),
        dbc.Col([
            dash_table.DataTable(
                data=df_pivot_year.to_dict('records'),
                page_size=15, 
                # sort_action='native',
                # filter_action='native',
                style_table={
                    'overflowX': 'auto'
                    }, 
                style_header={
                    'fontSize': 16,
                    'font-family':'system-ui',
                    'backgroundColor': 'rgb(80, 80, 80)',
                    'color': 'white',
                    'textAlign': 'center'
                    },
                style_data={
                    'fontSize': 16,
                    'font-family':'system-ui',
                    'backgroundColor': 'rgb(50, 50, 50)',
                    'color': 'white'
                    },
            ),
            dash_table.DataTable(
                data=df_pivot_month.to_dict('records'),
                page_size=10, 
                # sort_action='native',
                # filter_action='native',
                style_table={
                    'overflowX': 'auto'
                    }, 
                style_header={
                    'fontSize': 16,
                    'font-family':'system-ui',
                    'backgroundColor': 'rgb(80, 80, 80)',
                    'color': 'white',
                    'textAlign': 'center'
                    },
                style_data={
                    'fontSize': 16,
                    'font-family':'system-ui',
                    'backgroundColor': 'rgb(50, 50, 50)',
                    'color': 'white'
                    },
            ),
        ]),
    ]),
    dbc.Row([
        dbc.Col([
            dbc.Row([
                dbc.RadioItems(options=[{"label": y, "value": y} for y in yaxis_radio_buttons],
                            value='calories',
                            inline=True,
                            id='yaxis-radio-buttons')
            ]),
            dbc.Row([
                dbc.RadioItems(options=[{"label": x, "value": x} for x in xaxis_radio_buttons],
                            value='month',
                            inline=True,
                            id='xaxis-radio-buttons')
            ]),
            dbc.Row([
                dbc.RadioItems(options=[{"label": m, "value": m} for m in metric_radio_buttons],
                            value='avg',
                            inline=True,
                            id='metric-radio-buttons')
            ]),
            dbc.Row([
                dbc.RadioItems(options=[{"label": c, "value": c} for c in chart_radio_buttons],
                            value='histogram',
                            inline=True,
                            id='chart-radio-buttons')
            ]),
        ]),
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Graph(figure={}, id='peloton-graph-1')
        ]),
    ]),
])

# Add controls to build the interaction
@callback(
    Output(component_id='peloton-graph-1', component_property='figure'),
    Input(component_id='xaxis-radio-buttons', component_property='value'),
    Input(component_id='yaxis-radio-buttons', component_property='value'),
    Input(component_id='metric-radio-buttons', component_property='value'),
    Input(component_id='chart-radio-buttons', component_property='value'),
)
def update_graph(xaxis_chosen, yaxis_chosen, metric_chosen, chart_chosen):
    if chart_chosen == 'histogram':
        fig = px.histogram(
            df_table, 
            x = xaxis_chosen, 
            y = yaxis_chosen, 
            barmode = 'group', 
            height = 500, 
            histfunc = metric_chosen,
            template = 'plotly_dark',
            # text_auto=True,
            # nbins=(df['annual_periods'].nunique() * 2)
            )
        fig.update_layout(bargap=0.15)
    elif chart_chosen == 'pie':
        fig = px.pie(
            df_table,
            names = xaxis_chosen,
            values = yaxis_chosen
        )
    return fig