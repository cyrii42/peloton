from abc import ABC, abstractmethod
from dataclasses import dataclass, field

import pandas as pd

# from peloton.constants import MARIADB_DATABASE
# from peloton.helpers import create_mariadb_engine
# from peloton.peloton_pivots import PelotonPivots
# from peloton.peloton_processor import PelotonProcessor
# from peloton.peloton_ride import PelotonRide, PelotonRideGroup

from trash.peloton_sql import PelotonSQL


@dataclass
class PelotonRawData(ABC):
    df: pd.DataFrame
    sql: PelotonSQL

    @abstractmethod
    def export_to_sql(self):
        ...

    @abstractmethod
    def ingest_from_sql(self):
        ...

@dataclass
class PelotonRawWorkoutData(PelotonRawData):
    ...

@dataclass
class PelotonRawMetricsData(PelotonRawData):
    ...

@dataclass
class PelotonProcessedData(PelotonRawData):
    ...

@dataclass
class PelotonData():
    raw_workout_data: PelotonRawData
    raw_metrics_data: PelotonRawData
    processed_data: PelotonRawData
    new_workouts: bool = False
    new_workouts_num: int = field(init=False)
    df_pivots: pd.DataFrame = field(init=False)
    year_table: pd.DataFrame = field(init=False)
    month_table: pd.DataFrame = field(init=False)
    totals_table: pd.DataFrame = field(init=False)

'''
TYPES OF JOBS

`PelotonSQL`:  SQL data ingestion/export AND storing data from SQL
sql_engine: db.Engine

export_new_raw_workout_data_to_sql()
export_new_raw_metrics_data_to_sql()
export_new_processed_data_to_sql()
ingest_raw_workout_data_from_sql()
ingest_raw_metrics_data_from_sql()
ingest_processed_data_from_sql()


`PelotonData`:  Peloton data ingestion AND storing raw & processed Peloton data AND creating/storing pivots   - PelotonData
py_conn
new_workouts: bool
new_workouts_num: int
df_raw_workouts_data: pd.DataFrame
df_raw_metrics_data: pd.DataFrame
df_processed:  pd.DataFrame
df_pivots: pd.DataFrame
year_table: pd.DataFrame
month_table: pd.DataFrame
totals_table: pd.DataFrame

check_for_new_workouts()
pull_new_raw_metrics_data_from_peloton()
NEW:  pull_new_raw_workouts_data_from_peloton()  (previously included in check_for_new_workouts())
process_workouts_from_new_raw_data()
create_df_for_pivots()
create_year_table()
create_month_table()
create_totals_table()


PelotonPrinter:  Printing data to stdout
create_processed_table_for_stout()
print_processed_data_to_stdout()
print_pivot_tables()


PelotonCSV:  Writing data to CSV
write_csv_files()

PelotonGoogleSheets:  Writing data to Google Sheets
write_to_google_sheet()

'''

'''
PELOTON PROCESSOR
METHODS:





INSTANCE VARIABLES:





df_raw_workouts_data_in_sql (created in check_for_new_workouts)
df_raw_workout_data_new (created in check_for_new_workouts)
df_raw_workout_metrics_data_new (created in check_for_new_workouts)
'''

'''
PELOTON PIVOTS
METHODS






INSTANCE VARIABLES
peloton_processor (from __init__())

processed_table (from __init__())
spread = None (from __init__())
'''










'''
PELOTON PROCESSOR
METHODS:
check_for_new_workouts
pull_new_raw_metrics_data_from_peloton
export_new_raw_workout_data_to_sql
export_new_raw_metrics_data_to_sql
export_new_processed_data_to_sql
ingest_raw_workout_data_from_sql
ingest_raw_metrics_data_from_sql
ingest_processed_data_from_sql
print_processed_data_to_stdout
process_workouts_from_new_raw_data

INSTANCE VARIABLES:
sql_engine (from __init__())
new_workouts: bool (from __init__())
new_workouts_num: int (from __init__())
df_processed:  pd.DataFrame (from __init__())

py_conn (created in check_for_new_workouts)
df_raw_workouts_data_in_sql (created in check_for_new_workouts)
df_raw_workout_data_new (created in check_for_new_workouts)
df_raw_workout_metrics_data_new (created in check_for_new_workouts)
'''

'''
PELOTON PIVOTS
METHODS
create_processed_table_for_stout
create_df_for_pivots
create_year_table
create_month_table
create_totals_table
print_pivot_tables
write_csv_files
write_to_google_sheet

INSTANCE VARIABLES
peloton_processor (from __init__())
df_processed_workout_data (from __init__())
df_raw_workouts_data (from __init__())
df_raw_metrics_data (from __init__())
df_pivots (from __init__())
year_table (from __init__())
month_table (from __init__())
totals_table (from __init__())
processed_table (from __init__())
spread = None (from __init__())
'''



