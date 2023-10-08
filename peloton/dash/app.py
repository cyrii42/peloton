########### from: https://dash.plotly.com/tutorial ###########
#### https://plotly.com/python/
#### https://dash-bootstrap-components.opensource.faculty.ai/docs/themes/
###### run server with command:  gunicorn --reload -w 3 -b 0.0.0.0:9999 app:server   ########

# Import packages
import datetime as datetime

import dash
import dash_bootstrap_components as dbc
from dash import Dash, html

from peloton.dash.components import footer, navbar

# import peloton.dash.functions as dash_funcs
# import peloton.helpers as helpers
# import peloton.peloton_pivots as pivots

# mariadb_engine = helpers.create_mariadb_engine(database="peloton")

# df_table = dash_funcs.create_table_df(mariadb_engine)

# sql_data_for_pivots = pivots.get_sql_data_for_pivots(mariadb_engine)

# df_pivot_month = pivots.get_pivot_table_month(sql_data_for_pivots)

# df_pivot_year = pivots.get_pivot_table_year(sql_data_for_pivots)

# Initialize the app - incorporate css
app = Dash(
    __name__, 
    use_pages=True,
    external_stylesheets=[
        dbc.themes.SUPERHERO,
        dbc.icons.FONT_AWESOME
        ],
    meta_tags=[
        {   # check if device is a mobile device. This is a must if you do any mobile styling
            'name': 'viewport',
            'content': 'width=device-width, initial-scale=0.25'
        }
    ],
    suppress_callback_exceptions=False,
    title="Peloton Data - Dash"
)
server = app.server

def serve_layout():
    '''Define the layout of the application'''
    return html.Div(
        [
            # login_location,
            navbar,
            dbc.Container(
                dash.page_container,
                # class_name='my-2',
                fluid=True
            ),
            footer,
        ]
    )

app.layout = serve_layout  # set the layout to the serve_layout function

if __name__ == '__main__':
    app.run(debug=True, port=9999, host='0.0.0.0')