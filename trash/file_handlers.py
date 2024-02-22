import json
from dataclasses import dataclass
from pathlib import Path
from pprint import pprint
from zoneinfo import ZoneInfo

import pandas as pd
import sqlalchemy as db
from constants import PELOTON_CSV_DIR

from trash.pyloton_schema import PelotonWorkoutData

# from pyloton_schema import PelotonWorkoutData


EASTERN_TIME = ZoneInfo('America/New_York')
WORKOUTS_DIR = Path('../data/workouts').resolve()
INSTRUCTORS_JSON = Path('..').resolve().joinpath('peloton_instructors.json')


class PelotonSQL():
    def __init__(self, sql_engine: db.Engine):
        self.sql_engine = sql_engine

    def export_df_to_sql(self, input_df: pd.DataFrame, table_name: str) -> None:
        df = input_df.copy()
        
        for column in df.select_dtypes(exclude=['int64', 'float64', 'bool']).columns:
            df[column] = df[column].astype("string")
            
        with self.sql_engine.connect() as conn:
            df.to_sql(table_name, conn, if_exists="append", index=False)

    def ingest_df_from_sql(self, table_name: str) -> pd.DataFrame:
        with self.sql_engine.connect() as conn:
            df = pd.read_sql(f"SELECT * from {table_name}", conn)
            
        return df

    
@dataclass
class PelotonCSVWriter():
    peloton_data: PelotonWorkoutData

    def write_csv_files(self) -> None:
        self.peloton_data.year_table.to_csv(f"{PELOTON_CSV_DIR}/year_table.csv")
        self.peloton_data.month_table.to_csv(f"{PELOTON_CSV_DIR}/month_table.csv")
        self.peloton_data.totals_table.to_csv(f"{PELOTON_CSV_DIR}/totals_table.csv")
        self.peloton_data.df_processed_workout_data.to_csv(f"{PELOTON_CSV_DIR}/processed_workouts_data.csv")
        self.peloton_data.df_raw_workouts_data.to_csv(f"{PELOTON_CSV_DIR}/raw_workouts_data.csv")
        self.peloton_data.df_raw_metrics_data.to_csv(f"{PELOTON_CSV_DIR}/raw_metrics_data.csv")

class PelotonJSONWriter():
    def __init__(self):
        try:
            self.json_files = [file for file in WORKOUTS_DIR.iterdir()]
            self.workout_ids = [file.stem for file in WORKOUTS_DIR.iterdir()]
        except FileNotFoundError:
            self.json_files = list()
            self.workout_ids = list()
            
        self.total_workouts_on_disk = len(self.json_files)
        self.all_workouts = self.get_all_json_workouts()

    def get_workout_from_json(self, workout_id: str) -> PelotonWorkoutData:
        with open(WORKOUTS_DIR.joinpath(f"{workout_id}.json"), 'r') as f:
            return PelotonWorkoutData.model_validate_json(f)

    def get_all_json_workouts(self) -> list[PelotonWorkoutData]:
        if self.total_workouts_on_disk == 0:
            return list()
        else:
            return [self.get_workout_from_json(workout_id) for workout_id in self.workout_ids]

    def write_workout_to_json(self, workout: PelotonWorkoutData) -> None:
        with open(WORKOUTS_DIR.joinpath(f"{workout.workout_id}.json"), 'w') as f:
            json.dump(workout.model_dump(), f, indent=4)

    def get_instructors_dict_from_json(self) -> dict:
        try:
            with open(INSTRUCTORS_JSON, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return dict()

    def add_instructor_to_json(self, instructor: dict) -> None:
        instructors_dict = self.get_instructors_dict_from_json()
        instructors_dict.update({instructor['instructor_id']: instructor})
        with open(INSTRUCTORS_JSON, 'w') as f:
            json.dump(instructors_dict, f, indent=4)

# @dataclass
# class PelotonGoogleSheetsWriter():
#     data: PelotonProcessor
#     spread: Spread = field(init=False)

#     def __post_init__(self):
#         self.spread = Spread(PELOTON_SPREADSHEET)

#     def write_to_google_sheet(self) -> None:
#         worksheets = {
#             'Processed Data': self.data.ingest_processed_data_from_sql(),
#             'Raw Metrics Data': self.data.ingest_raw_metrics_data_from_sql(),
#             'Raw Workouts Data': self.data.ingest_raw_workout_data_from_sql(),
#             'Year Table': self.data.pivots.year_table,
#             'Month Table': self.data.pivots.month_table,
#             'Totals Table': self.data.pivots.totals_table
#         }

#         for sheet_name, sheet_df in worksheets.items():
#             last_existing_row = sheet_df.shape[0] + 1
#             starting_row = last_existing_row + 1

#             self.spread.df_to_sheet(sheet_df, 
#                                sheet=sheet_name, 
#                                replace=True, 
#                                index=False, 
#                                headers=True, 
#                                freeze_headers=True, 
#                                start=(1, 1))

# class PelotonPrinter():
#     def __init__(self, df_processed: pd.DataFrame):
#         self.df_processed = df_processed
#         self.pivots = PelotonPivots(df_processed)

#     def regenerate_tables(self, new_df_processed: pd.DataFrame) -> None:
#         self.df_processed = new_df_processed
#         self.pivots = PelotonPivots(new_df_processed)
        
#     def print_processed_data(self) -> None:
#         df = self.df_processed
#         if isinstance(df['start_time_iso'].dtype, pd.DatetimeTZDtype):
#             df['start_time_strf'] = [x.tz_convert(ZoneInfo("America/New_York")).strftime('%a %h %d %I:%M %p') 
#                                         for x in df['start_time_iso'].tolist()]
#         else:
#             df['start_time_strf'] = [datetime.fromisoformat(x).strftime('%a %h %d %I:%M %p') 
#                                         for x in df['start_time_iso'].tolist()]
#         print("")
#         print(df[['start_time_strf', 'ride_title', 'instructor_name', 'total_output', 
#                     'distance', 'calories', 'heart_rate_avg', 'strive_score']].tail(15))

#     def print_pivot_tables(self) -> None:
#         print("")
#         print("                             GRAND TOTALS")
#         print(self.pivots.totals_table)
#         print("")
#         print(self.pivots.year_table)
#         print("")
#         print(self.pivots.month_table)

def main():
    json_writer = PelotonJSONWriter()
    # asdf = json_writer.get_workout_from_json('9ae7e95d7087420a8fe1a8393fb11d1f')
    # pprint(asdf)

    asdf = json_writer.get_instructors_dict_from_json()
    print(asdf)


if __name__ == '__main__':
    main()