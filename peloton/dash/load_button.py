from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import sqlalchemy as db
from utils import ids
from peloton_to_mariadb import calculate_new_workouts_num, get_new_workouts

def render(app: Dash) -> html.Div:
    @app.callback(
        Output(ids.NATION_DROPDOWN, "value"),
        Input(ids.LOAD_NEW_DATA_BUTTON, "n_clicks"),
    )
    def load_mariadb_data(_: int, engine: db.Engine) -> pd.DataFrame():
        with engine.connect() as conn:
            mariadb_df = pd.read_sql("SELECT * from peloton",conn,index_col='start_time_iso',parse_dates=['start_time_iso', 'start_time_local'])

        new_workouts_num = calculate_new_workouts_num(mariadb_df)

        if new_workouts_num > 0:
            new_entries = get_new_workouts(new_workouts_num)
            with engine.connect() as conn:
                new_entries.to_sql("peloton", conn, if_exists="append", index=False)

    return html.Div(
        children=[
            html.H6("Nation"),
            dcc.Dropdown(
                id=ids.NATION_DROPDOWN,
                options=[{"label": year, "value": year} for year in all_nations],
                value=all_nations,
                multi=True,
            ),
            html.Button(
                className="dropdown-button",
                children=["Select All"],
                id=ids.SELECT_ALL_NATIONS_BUTTON,
                n_clicks=0,
            ),
        ]
    )
