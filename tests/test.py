from pylotoncycle import pylotoncycle
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import sqlite3
import pandas as pd
import sqlalchemy as db
from config import eastern_time, mariadb_user, mariadb_pass, mariadb_server

# Create SQLite database
# sql_conn = sqlite3.connect(f"{str(datetime.now().strftime('%Y-%m-%d_%H-%M'))}_peleton_data_test.db")
# sql_conn = sqlite3.connect("/mnt/home-ds920/peloton_workouts.db")

mariadb_database = "zmv"
sql_conn = db.create_engine(
    f'mysql+pymysql://{mariadb_user}:{mariadb_pass}@{mariadb_server}/{mariadb_database}?charset=utf8mb4').connect()

# Create Pandas DataFrame from existing table
with sql_conn as conn:
    db_dataframe = pd.read_sql("SELECT * from peloton", conn, index_col='start_time_iso', parse_dates=['start_time_iso', 'start_time_local'])

print(db_dataframe)

print(db_dataframe.shape[0]) 