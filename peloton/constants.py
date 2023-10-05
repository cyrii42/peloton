import os
from zoneinfo import ZoneInfo
from dotenv import load_dotenv

load_dotenv()

# Time zone setup
EASTERN_TIME = ZoneInfo("America/New_York")

# InfluxDB setup
INFLUX_URL = "http://mac-mini.box:8086"
INFLUX_ORG = "ZMV"
INFLUX_TOKEN_HASS = os.getenv("INFLUX_TOKEN_HASS") # Home Assistant read-only
INFLUX_TOKEN_CONED = os.getenv("INFLUX_TOKEN_CONED") # Con Edison token

# Home Assistant MariaDB setup
MARIADB_SERVER = os.getenv("MARIADB_HASS_IP")
MARIADB_USER = os.getenv("MARIADB_USERNAME_PYTHON")
MARIADB_PASS = os.getenv("MARIADB_PASSWORD_PYTHON")

# PylotonCycle setup
PELOTON_USERNAME = os.getenv("PELOTON_USERNAME")
PELOTON_PASSWORD = os.getenv("PELOTON_PASSWORD")