from zoneinfo import ZoneInfo
from datetime import datetime
import sqlalchemy as db
from dotenv import load_dotenv
import os

load_dotenv()

# Time zone setup & UTC offset functions
eastern_time = ZoneInfo("America/New_York")

class NaiveDatetimeError(Exception):
    def __init__(self, dt, message="Input datetime object is not timezone-aware"):
        self.dt = dt
        self.message = message
        super().__init__(self.message)

def utc_offset_int(dt: datetime=datetime.now()) -> int:
    if dt.utcoffset() != None:
        return int((dt.utcoffset().seconds / 60 / 60) - 24)
    else: 
        raise NaiveDatetimeError(dt)

def utc_offset_str(dt: datetime=datetime.now()) -> str:
    if dt.utcoffset() != None:
        utc_offset_int = int((dt.utcoffset().seconds / 60 / 60) - 24)
        if utc_offset_int >= 0:
            return f"0{utc_offset_int}:00"
        else:
            return f"-0{abs(utc_offset_int)}:00"
    else: 
        raise NaiveDatetimeError(dt)
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
mariadb_engine = db.create_engine(
    f"mysql+pymysql://{mariadb_user}:{mariadb_pass}@{mariadb_server}/{mariadb_database}?charset=utf8mb4")

# PylotonCycle setup
peloton_username = os.getenv("PELOTON_USERNAME")
peloton_password = os.getenv("PELOTON_PASSWORD")
