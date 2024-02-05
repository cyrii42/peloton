import os
from zoneinfo import ZoneInfo

from dotenv import load_dotenv

load_dotenv()

# Time zone setup
EASTERN_TIME = ZoneInfo("America/New_York")

# InfluxDB setup
INFLUX_URL = os.getenv("INFLUX_URL") 
INFLUX_ORG = os.getenv("INFLUX_ORG")
INFLUX_TOKEN_HASS = os.getenv("INFLUX_TOKEN_HASS") # Home Assistant read-only
INFLUX_TOKEN_CONED = os.getenv("INFLUX_TOKEN_CONED") # Con Edison token

# Home Assistant MariaDB setup
MARIADB_SERVER = os.getenv("MARIADB_HASS_IP")
MARIADB_USER = os.getenv("MARIADB_USERNAME_PYTHON")
MARIADB_PASS = os.getenv("MARIADB_PASSWORD_PYTHON")
MARIADB_DATABASE = "peloton"
PELOTON_EXCEL_FILE = os.getenv("PELOTON_EXCEL_FILE")

# PylotonCycle setup
PELOTON_USERNAME = os.getenv("PELOTON_USERNAME")
PELOTON_PASSWORD = os.getenv("PELOTON_PASSWORD")
PELOTON_CSV_DIR = os.getenv("PELOTON_CSV_DIR")
PELOTON_SPREADSHEET = os.getenv("PELOTON_SPREADSHEET")