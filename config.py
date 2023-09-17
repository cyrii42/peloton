from zoneinfo import ZoneInfo
import sqlalchemy as db
from pylotoncycle import pylotoncycle
from dotenv import load_dotenv
import os

load_dotenv()

# Time zone setup
eastern_time = ZoneInfo("America/New_York")

# InfluxDB setup
influx_url = "http://mac-mini.box:8086"
influx_org = "ZMV"
influx_token_hass = os.getenv("INFLUX_TOKEN_HASS") # Home Assistant read-only
influx_token_coned = os.getenv("INFLUX_TOKEN_CONED") # Con Edison token

# MariaDB setup
mariadb_server = "10.0.0.200"
mariadb_database = "zmv"
mariadb_user = os.getenv("MARIADB_USERNAME_PYTHON")
mariadb_pass = os.getenv("MARIADB_PASSWORD_PYTHON")
mariadb_conn = db.create_engine(
    f'mysql+pymysql://{mariadb_user}:{mariadb_pass}@{mariadb_server}/{mariadb_database}?charset=utf8mb4').connect()

# PylotonCycle setup
username = os.getenv("PELOTON_USERNAME")
password = os.getenv("PELOTON_PASSWORD")
py_conn = pylotoncycle.PylotonCycle(username, password)
