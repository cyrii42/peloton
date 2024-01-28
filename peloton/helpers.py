import json
import os
import platform
from datetime import datetime

import pandas as pd
import sqlalchemy as db
from pylotoncycle import PylotonCycle

import peloton.constants as const


# SQL database functions
def create_mariadb_engine(database: str) -> db.Engine:
    mariadb_url = db.URL.create(
        drivername="mysql+pymysql",
        username=const.MARIADB_USER,
        password=const.MARIADB_PASS,
        host=const.MARIADB_SERVER,
        username=const.MARIADB_USER,
        password=const.MARIADB_PASS,
        host=const.MARIADB_SERVER,
        database=database,
    )
    return db.create_engine(mariadb_url)


def select_all_from_table(
    engine: db.Engine, table: str, index_col: str = None, parse_dates: list[str] = None
) -> pd.DataFrame:
    with engine.connect() as conn:
        df = pd.read_sql(
            f"SELECT * from {table}", conn, index_col=index_col, parse_dates=parse_dates
        )
    return df


# UTC offset functions
class NaiveDatetimeError(Exception):
    def __init__(self, dt, message="Input datetime object is not timezone-aware"):
        self.dt = dt
        self.message = message
        super().__init__(self.message)


def utc_offset_int(dt: datetime = datetime.now()) -> int:
    if dt.utcoffset() != None:
        return int((dt.utcoffset().seconds / 60 / 60) - 24)
    else: 
        raise NaiveDatetimeError(dt)


def utc_offset_str(dt: datetime = datetime.now()) -> str:
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