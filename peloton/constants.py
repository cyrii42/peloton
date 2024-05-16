import os
from zoneinfo import ZoneInfo
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# Time zone setup
EASTERN_TIME = ZoneInfo("America/New_York")

# MongoDB setup
MONGODB_CONNECTION_STRING = os.getenv("MONGODB_CONNECTION_STRING")
MONGODB_DATABASE = 'peloton'
MONGODB_COLLECTION = 'peloton'
MONGODB_INSTRUCTORS_COLLECTION = 'peloton_instructors'
MONGODB_HOSTNAME = os.getenv("MONGODB_HOSTNAME")

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
PELOTON_BASE_URL = "https://api.onepeloton.com"

# Path objects
# ROOT_DIR = Path.home().joinpath('python', 'peloton')
ROOT_DIR = Path.cwd()
DATA_DIR = ROOT_DIR.joinpath('data')
WORKOUTS_DIR = ROOT_DIR.joinpath('data', 'workouts')
SESSION_JSON = ROOT_DIR.joinpath('session_id.json')
INSTRUCTORS_JSON = ROOT_DIR.joinpath('peloton_instructors.json')

SQLITE_FILENAME = f"sqlite:///{DATA_DIR.joinpath('peloton.db').resolve()}"

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
    'fitness_discipline': 'string',
    'ride_id': 'string',
    'instructor_json': 'string',
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
    'hr_zone5': 'int64',
    'output_per_min': 'float64',
    'duration_hrs': 'float64',
}

INSTRUCTOR_NAMES_DICT = {
    '0021e2220a7940cf94a7647b1e4bae6c': 'Chelsea Jackson Roberts',
    '017dd08b095346979ddf761eb49f9f67': 'Erik Jäger',
    '01f636dc54a145239c4348e1736684ee': 'Bradley Rose',
    '040ab78d62a74cfc9954c0e320815993': 'Selena Samuela',
    '048f0ce00edb4427b2dced6cbeb107fd': 'Jess King',
    '05735e106f0747d2a112d32678be8afd': 'Olivia Amato',
    '0ac29effd55a435bad2f5c07cab8e567': 'Charlotte Weidenbach',
    '0e836f86aa9c488782452243f2e17170': 'Mayla Wedekind',
    '15f01c9145de4d21b58c1a3e4e44a486': 'Alex Karwoski',
    '1697e6f580494740a5a1ca62b8b3f47c': 'Rad Lopez',
    '16f7a0fa5ee64e1f8fc050c8a903ac9b': 'Assal Arian',
    '1b79e462bd564b6ca5ec728f1a5c2af0': 'Jess Sims',
    '1e59e949a19341539214a4a13ea7ff01': 'Denis Morton',
    '1f4d39cd181c4805a00cd0a53f6c9562': 'Ash Pryor',
    '23d0e395f6b843ec8a21c0305bac4696': 'Mariana Fernández',
    '255c81782f7242c9a6ba52e0a5f54912': 'Callie Gullickson',
    '286fc17080d34406a54b80ad8ff83e12': 'Becs Gentry',
    '2e57092bee334c8c8dcb9fe16ba5308c': 'Alex Toussaint',
    '304389e2bfe44830854e071bffc137c9': 'Matt Wilpers',
    '3126fe699a69419882b96172ffbbe604': 'Jeffrey McEachern',
    '35016225e39d46dbbc364991ab48e10f': 'Christian Vande Velde',
    '3ff679ebbd324c83a8ab6cfa6bb4be37': 'Hannah Frankson',
    '4672db841da0495caf4b8f9cda405512': 'Sam Yo',
    '4904612965164231a37143805a387e40': 'Kendall Toole',
    '51702da3a4684b988d31d89eebb43175': 'Jenn Sherman',
    '561f95c405734d8488ed8dcc8980d599': 'Hannah Corbin',
    '5a19bfe66e644a2fa3e6387a91ebc5ce': "Christine D'Ercole",
    '5b9a37522b094730927d3eb538ab0056': 'Susie Chan',
    '696bd08dd5284accab065e2147b121d7': 'Camila Ramón',
    '6c4b9f8582b84ab1bb1225d3e396e92e': 'Kirra Michel',
    '731d7b7f6b414a49892c21f01e25317d': 'Ally Love',
    '76e245b7a0fa42b4a1cd41576943e788': 'Logan Aldridge',
    '788569c2e088412799659a4f9ee334e2': 'Marcel Maurer',
    '7bb6ed1c35134642a9fe019c491c32b5': 'Jermaine Johnson',
    '7f3de5e78bb44d8591a0f77f760478c3': 'Ben Alldis',
    '9c67c1b94e5d4ad5a1cbe439ac62eb75': 'Irène Kaymer',
    'a4b1a372a14a442cb2d729dc34bd2596': 'Ross Rayburn',
    'a606b2c39c194bcc80f9a541b97b4537': 'Matty Maggiacomo',
    'a8c56f162c964e9392568bc13828a3fb': 'Anna Greenberg',
    'accfd3433b064508845d7696dab959fd': 'Benny Adami',
    'b8c2734e18a7496fa146b3a42465da67': 'Aditi Shah',
    'baf5dfb4c6ac4968b2cb7f8f8cc0ef10': 'Cody Rigsby',
    'bbbfd7c4f0ad4c138eeb7787bf63104f': 'Jon Hosking',
    'c0a9505d8135412d824cf3c97406179b': 'Leanne Hainsby',
    'c406f36aa2a44a5baf8831f8b92f6920': 'Robin Arzón',
    'c8f95daedc2c4291a12008153a977661': 'Kirsten Ferguson',
    'c9bd86e59b9b4f96981848467838aa9c': 'Tunde Oyeneyin',
    'c9d46b17357e44eea8cebed3a675f743': 'Nico Sarani',
    'c9fa21c2004c4544a7c35c28a6196c77': 'Andy Speer',
    'dc535671e06546d399575c595671b603': 'Tobias Heinze',
    'e2b47232c29844c380f0a5374317a3c9': 'Mila Lazar',
    'e2e6586d898d4422b3f6e3a259ff3f90': 'Cliff Dwenger',
    'ee70149e6dca4d72a59154f592c5e5f2': 'Katie Wang',
    'efd71bafb8c544e98a8d3882531f2976': 'Rebecca Kennedy',
    'f0b16be6d296405d901595f468520f69': 'Marcel Dinkins',
    'f48347e0fb3748c08aa6c6e031b48897': 'Kristin McGee',
    'f6f2d613dc344e4bbf6428cd34697820': 'Emma Lovewell',
    'f962a2b1b34d424cabab73bef81bc8db': 'Adrian Williams',
    'ff78b43e8115485f9cb4e153dba8e986': 'Joslyn Thompson Rule'
}