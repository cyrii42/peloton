import os
from zoneinfo import ZoneInfo
from pathlib import Path

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
PELOTON_USER_ID = os.getenv("PELOTON_USER_ID")
PELOTON_CSV_DIR = os.getenv("PELOTON_CSV_DIR")
PELOTON_SPREADSHEET = os.getenv("PELOTON_SPREADSHEET")

# Path objects
# ROOT_DIR = Path.home().joinpath('python', 'peloton')
ROOT_DIR = Path.cwd()
DATA_DIR = Path.cwd().joinpath('data')
INSTRUCTORS_JSON = ROOT_DIR.joinpath('peloton_instructors.json')
WORKOUTS_DIR = ROOT_DIR.joinpath('data', 'workouts')
SESSION_JSON = ROOT_DIR.joinpath('session_id.json')
BASE_URL = "https://api.onepeloton.com"
SQLITE_FILENAME = f"sqlite:///{ROOT_DIR.joinpath('data', 'peloton.db').resolve()}"

DF_DTYPES_DICT = {
    'workout_id': 'string', 
    'start_time': 'datetime64[ns, America/New_York]', 
    'end_time': 'datetime64[ns, America/New_York]', 
    'metrics_type': 'string', 
    'workout_type': 'string', 
    'leaderboard_rank': 'int64',
    'total_leaderboard_users': 'int64', 
    'average_effort_score': 'float64', 
    'title': 'string', 
    'description': 'string', 
    'ride_duration': 'int64', 
    'ride_length': 'int64', 
    'image_url': 'string', 
    'difficulty_estimate': 'float64',  
    'instructor_id': 'string', 
    'instructor_name': 'string', 
    'avg_output': 'int64', 
    'avg_cadence': 'int64', 
    'avg_resistance': 'int64',  
    'avg_speed': 'float64', 
    'avg_heart_rate': 'int64',
    'max_output': 'int64', 
    'max_cadence': 'int64', 
    'max_resistance': 'int64',  
    'max_speed': 'float64', 
    'max_heart_rate': 'int64', 
    'total_output': 'int64', 
    'distance': 'float64', 
    'calories': 'int64',  
    'hr_zone1': 'int64', 
    'hr_zone2': 'int64', 
    'hr_zone3': 'int64', 
    'hr_zone4': 'int64', 
    'hr_zone5': 'int64'
}