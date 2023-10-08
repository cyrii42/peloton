# notes
'''
This file is for creating a simple footer element.
This component will sit at the bottom of each page of the application.
'''

import dash_bootstrap_components as dbc
# package imports
from dash import html

footer = html.Footer(
    dbc.Container(
        [
            html.Hr(),
            'Footer item 1',
            # html.Br(),
            # 'Footer item 2',
            # html.Br(),
            # 'Footer item 3'
        ]
    )
)
