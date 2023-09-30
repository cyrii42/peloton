from zoneinfo import ZoneInfo
from datetime import datetime
import json
import os
import platform
from dotenv import load_dotenv
import sqlalchemy as db

load_dotenv()

# Time zone setup & UTC offset functions
EASTERN_TIME = ZoneInfo("America/New_York")


def check_hostname() -> str:
    if platform.system() == "Windows":
        return platform.uname().node
    else:
        return os.uname()[1]


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


def jprint(obj: dict):
    # create a formatted string of the Python JSON object
    text = json.dumps(obj, sort_keys=True, indent=2)
    print(text)
    

def check_dir(subdir: str) -> bool:
    if subdir in os.getcwd():
        print("We're in the right directory!  Continuing...")
        return True
    elif "python" in os.getcwd():
        if subdir in os.listdir(path='.'):
            print(f"Changing to \'{subdir}\' directory...")
            os.chdir(f"./{subdir}")
            return True
        else:
            print(f"Couldn't find the \'{subdir}\' directory.  Bailing out.")
            return False
    else:
        if "python" in os.listdir(path='.'):
            print("Changing to 'python' directory...")
            os.chdir("./python")
            if subdir in os.listdir(path='.'):
                print(f"Changing to \'{subdir}\' directory...")
                os.chdir(f"./{subdir}")
                return True
            else:
                print(f"Couldn't find the \'{subdir}\' directory.  Bailing out.")
                return False
        else:
            print("Couldn't find the 'python' directory.  Bailing out.")
            return False
        

# InfluxDB setup
INFLUX_URL = "http://mac-mini.box:8086"
INFLUX_ORG = "ZMV"
INFLUX_TOKEN_HASS = os.getenv("INFLUX_TOKEN_HASS") # Home Assistant read-only
INFLUX_TOKEN_CONED = os.getenv("INFLUX_TOKEN_CONED") # Con Edison token
INFLUX_BUCKET_CONED = "conedison"
INFLUX_BUCKET_HASS = "homeassistant"

# Home Assistant MariaDB setup
MARIADB_SERVER = os.getenv("MARIADB_HASS_IP")
MARIADB_DATABASE_HASS = "homeassistant"
MARIADB_DATABASE_ZMV = "zmv"
MARIADB_USER = os.getenv("MARIADB_USERNAME_PYTHON")
MARIADB_PASS = os.getenv("MARIADB_PASSWORD_PYTHON")
MARIADB_ENGINE_HASS = db.create_engine(
    f'mysql+pymysql://{MARIADB_USER}:{MARIADB_PASS}@{MARIADB_SERVER}/{MARIADB_DATABASE_HASS}?charset=utf8mb4')
MARIADB_ENGINE_ZMV = db.create_engine(
    f'mysql+pymysql://{MARIADB_USER}:{MARIADB_PASS}@{MARIADB_SERVER}/{MARIADB_DATABASE_ZMV}?charset=utf8mb4')

# Tautulli setup
TAUTULLI_URL = os.getenv("TAUTULLI_URL")
TAUTULLI_API_KEY = os.getenv("TAUTULLI_API_KEY")

# PylotonCycle setup
PELOTON_USERNAME = os.getenv("PELOTON_USERNAME")
PELOTON_PASSWORD = os.getenv("PELOTON_PASSWORD")