import os
import platform
import json
import sqlalchemy as db
import pandas as pd
from datetime import datetime
from utils.constants import MARIADB_USER, MARIADB_PASS, MARIADB_SERVER


# SQL database functions
def create_mariadb_engine(database: str) -> db.Engine:
    mariadb_url = db.URL.create(
        "mysql+pymysql",
        username=MARIADB_USER,
        password=MARIADB_PASS,
        host=MARIADB_SERVER,
        database=database,
    )
    return db.create_engine(mariadb_url)

def get_peloton_data_from_sql(engine: db.Engine) -> pd.DataFrame:
    with engine.connect() as conn:
        df = pd.read_sql(
            "SELECT * from peloton",
            conn,
            index_col='start_time_iso',
            parse_dates=['start_time_iso', 'start_time_local']
            )
    return df


def export_peloton_data_to_sql(input_df: pd.DataFrame, engine: db.Engine):
     with engine.connect() as conn:
        input_df.to_sql("peloton", conn, if_exists="append", index=False)


# UTC offset functions
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


# Miscellaneous functions
def check_hostname() -> str:
    if platform.system() == "Windows":
        return platform.uname().node
    else:
        return os.uname()[1]
    

def jprint(obj: dict):
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