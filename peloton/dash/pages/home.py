import dash
import dash_bootstrap_components as dbc
import plotly.express as px
from dash import Input, Output, callback, dash_table, dcc, html

import peloton.dash.utils.functions as dash_funcs
import peloton.helpers as helpers
import peloton.peloton_pivots as pivots

dash.register_page(
    __name__,
    path='/',
    redirect_from=['/home'],
    title='Peloton Data - Dash'
)

layout = html.Div([
    html.H1('Home page!'),
    html.Div([
        html.P('Some test text here.'),
        html.A('Checkout the Peloton Data page here.', href='/peloton'),
        dcc.Markdown('''
            Check out the Peloton Data page [here!](/peloton)
        '''),
        dcc.RadioItems(
            id='radios',
            options=[{'label': i, 'value': i} for i in ['Orange', 'Blue', 'Red']],
            value='Orange',
        ),
    ], id='content'),
])