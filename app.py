########### from: https://dash.plotly.com/tutorial ###########
#### https://plotly.com/python/
#### https://dash-bootstrap-components.opensource.faculty.ai/docs/themes/
###### run server with command:  gunicorn --reload -w 3 -b 0.0.0.0:9999 app:server   ########

# Import packages
import datetime
from dash import Dash, html, dash_table, dcc, callback, Output, Input
import pandas as pd
import sqlite3
import plotly.express as px
import dash_bootstrap_components as dbc
# import dash_mantine_components as dmc
from config import eastern_time, mariadb_conn

# Create Pandas DataFrame from existing table (removed index_col='start_time_iso')
with mariadb_conn as conn:
    df = pd.read_sql("SELECT * from peloton", conn, parse_dates=['start_time_iso', 'start_time_local'])

# Add additional metrics
df['min'] = [round((x / 60),0) for x in df['duration'].tolist()]
df['length_min'] = [round((x / 60),0) for x in df['length'].tolist()]
df['output/min'] = [round((x[0] / (x[1] / 60)),2) for x in zip(df['output'].tolist(), df['duration'].tolist())]
df['start_time'] = [x.strftime('%b %-d, %Y %-I:%M %p') for x in df['start_time_iso'].tolist()]

df['annual_periods'] = [x.to_period(freq='Y') for x in df['start_time_iso'].tolist()]
df['monthly_periods'] = [x.to_period(freq='M') for x in df['start_time_iso'].tolist()]
df['month_name'] = [x.strftime('%B %Y') for x in df['start_time_iso'].tolist()]
# df['weekly_periods'] = [x.to_period(freq='W') for x in df['start_time_iso'].tolist()]

# Initialize the app - incorporate css
external_stylesheets = [dbc.themes.SUPERHERO]
app = Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
app.title = "Peloton Data - Dash"

# Define list of columns for datatable
table_column_list = [
    'start_time_local',
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
    'effort_points'
    ]

xaxis_radio_buttons = [
    'month_name',
    'start_time_local',
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

# App layout
app.layout = dbc.Container([
    dbc.Row([
        html.Div("Zach's Peloton Data", className="text-primary text-center fs-3")
    ]),
    
    # dbc.Row([
    #     html.Div('Charts here', className="text-primary text fs-4")
    # ]),

    dbc.Row([
        dbc.Col(),
        dbc.Col([
            dbc.Row([
                dbc.RadioItems(options=[{"label": y, "value": y} for y in yaxis_radio_buttons],
                            value='calories',
                            inline=True,
                            id='yaxis-radio-buttons')
            ]),
        
            dbc.Row([
                dbc.RadioItems(options=[{"label": x, "value": x} for x in xaxis_radio_buttons],
                            value='month_name',
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

    # dbc.Row([
    #         dcc.Graph(figure={}, id='my-first-graph-final')
    #     ]),

    # dbc.Row([
    #         dash_table.DataTable(data=df[column_list].to_dict('records'), page_size=25, style_table={'overflowX': 'auto'})
    #     ]),
    
    dbc.Row([
        dbc.Col([
            dash_table.DataTable(
                data=df[table_column_list].sort_values(by='start_time_local', ascending=False).to_dict('records'),
                page_size=20, 
                sort_action='native',
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
                style_cell_conditional=[
                    {
                        'if': {'column_id': ['instructor', 'start_time_local', 'title']},
                        'textAlign': 'left'
                    }
                ]
            )
        ], width=6),

        dbc.Col([
            dcc.Graph(figure={}, id='my-first-graph-final')
        ], width=6),
    ]),

], fluid=True)


# Add controls to build the interaction
@callback(
    Output(component_id='my-first-graph-final', component_property='figure'),
    Input(component_id='xaxis-radio-buttons', component_property='value'),
    Input(component_id='yaxis-radio-buttons', component_property='value'),
    Input(component_id='metric-radio-buttons', component_property='value'),
    Input(component_id='chart-radio-buttons', component_property='value'),
)
def update_graph(xaxis_chosen, yaxis_chosen, metric_chosen, chart_chosen):
    if chart_chosen == 'histogram':
        fig = px.histogram(
            df, 
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
            df,
            names = xaxis_chosen,
            values = yaxis_chosen
        )
    return fig

# Run the app
if __name__ == '__main__':
    app.run(debug=True, port=9999, host='0.0.0.0')
    # app.run_server(debug=True)