########### from: https://dash.plotly.com/tutorial ###########
#### https://plotly.com/python/
#### https://plotly.com/python/plotly-express/ 
#### https://dash-bootstrap-components.opensource.faculty.ai/docs/themes/
###### run server with command:  gunicorn --reload -w 3 -b 0.0.0.0:9988 app-weight-log:server   ########

#### https://influxdb-client.readthedocs.io/en/stable/index.html
#### https://github.com/influxdata/influxdb-client-python

# Import packages

import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from dash import Input, Output, callback, dash_table, dcc, html, register_page

import peloton.dash.utils.weight_log_influx as funcs

register_page(
    __name__,
    title='Weight Log Data - Dash'
)

# range_start_time_str = funcs.get_range_start_str(90)

df = funcs.influx_query_weight("2010-10-04T00:00:00Z")
df = df.drop(columns=['result', 'table', '_start', '_stop', '_measurement', 'domain', 'entity_id', 'friendly_name', 'source'])
df = df.rename(columns={'_time': 'time', 'value': 'weight'})

df['weight'] = [round(x, 2) for x in df['weight'].tolist()]
df['avg'] = df['weight'].ewm(span=10).mean().round(2)
df['time_dt'] = [pd.to_datetime(x) for x in df['time'].tolist()]
df['date'] = [x.strftime('%b %-d, %Y') for x in df['time_dt'].tolist()]

df = df.set_index('time')

# Define list of columns for datatable
table_column_list = [
    'time_dt',
    'date',
    'weight',
    'avg',
]

# Define lists of columns for charts
yaxis_radio_buttons = [
    'avg',
    'weight',
    ]

layout = html.Div([
    dbc.Row([
        html.Div("Zach's Weight Log Data", className="text-primary text-center fs-3")
    ]),
    
    dbc.Row([
        dbc.RadioItems(options=[{"label": y, "value": y} for y in yaxis_radio_buttons],
                    value='avg',
                    inline=True,
                    id='yaxis-radio-buttons')
        # dcc.RangeSlider(min(df_weight_avg['_time']), max(df_weight_avg['_time']), 1, value=[5, 15], id='my-range-slider'),
    ]),
    
    dbc.Row([
        dbc.Col([
            dash_table.DataTable(
                data=df[table_column_list].sort_values(by='time_dt', ascending=False).drop(columns=['time_dt']).to_dict('records'),
                page_size=15, 
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
                style_cell_conditional=[
                    {
                        'if': {'column_id': ['instructor', 'start_time_local', 'title']},
                        'textAlign': 'left'
                    }
                ]
            ),
        ], width=4),

        dbc.Col([
            dcc.Graph(figure={}, id='weightlog-graph-1')
        ], width=8),
    ]),
])


# Add controls to build the interaction
@callback(
    Output(component_id='weightlog-graph-1', component_property='figure'),
    Input(component_id='yaxis-radio-buttons', component_property='value')
)
def update_graph(y_chosen):
    fig = px.line(
        df, 
        x = 'time_dt', 
        y = y_chosen,
        title = "Zach's Weight Log Chart",
        # barmode = 'group', 
        height = 600, 
        # histfunc = metric_chosen,
        template = 'plotly_dark',
        # text_auto=True,
        # nbins=(df['annual_periods'].nunique() * 2)
        )
    # fig.update_layout(bargap=0.15)
    return fig