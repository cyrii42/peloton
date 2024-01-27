from datetime import datetime
import argparse
from dataclasses import dataclass, field

import pandas as pd
import sqlalchemy as db
from pylotoncycle import PylotonCycle

import peloton.constants as const
import peloton.functions as func
import peloton.helpers as helpers
from peloton.peloton_pivots import PelotonPivots

DATABASE = const.MARIADB_DATABASE


def create_pyltotoncycle_conn() -> PylotonCycle:
    return PylotonCycle(const.PELOTON_USERNAME, const.PELOTON_PASSWORD) 


@dataclass
class PelotonProcessor():
    sql_engine: db.Engine
    py_conn: PylotonCycle = field(default_factory=create_pyltotoncycle_conn)
    new_workouts: bool = False
    df_raw_workouts_data_in_sql: pd.DataFrame = field(init=False)
    new_workouts_num: int = field(init=False, default=0)
    df_raw_workout_data_new: pd.DataFrame = field(init=False)
    df_raw_workout_metrics_data_new: pd.DataFrame = field(init=False)
    df_processed: pd.DataFrame = field(init=False)

    def __post_init__(self) -> None:
        # Pull raw workout data from MariaDB and use it to calculate the number of new Peloton workouts
        self.df_raw_workouts_data_in_sql = helpers.ingest_raw_workout_data_from_sql(self.sql_engine)
        self.new_workouts_num = func.calculate_new_workouts_num(self.py_conn, self.df_raw_workouts_data_in_sql)
        self.new_workouts = True if self.new_workouts_num > 0 else False
    
    def pull_from_peloton_and_write_to_sql(self) -> None:
        if self.new_workouts:
            # Pull new workout data from Peloton
            print(f"Pulling data for {self.new_workouts_num} new workouts from Peleton...\n")
            self.df_raw_workout_data_new = func.pull_new_raw_workouts_data_from_peloton(self.py_conn, self.new_workouts_num)
            self.df_raw_workout_metrics_data_new = func.pull_new_raw_metrics_data_from_peloton(self.py_conn, self.df_raw_workout_data_new)

            # Write the new raw data to SQL
            helpers.export_raw_workout_data_to_sql(self.df_raw_workout_data_new, self.sql_engine)
            helpers.export_raw_metrics_data_to_sql(self.df_raw_workout_metrics_data_new, self.sql_engine)
            
            # Process the new raw data
            self.df_processed = func.process_workouts_from_raw_data(self.df_raw_workout_data_new, self.df_raw_workout_metrics_data_new)

            # Write the new processed data to SQL
            helpers.export_processed_data_to_sql(self.df_processed, self.sql_engine)

@dataclass
class PivotCSVWriter():
    pivots: PelotonPivots
    peloton_processor: PelotonProcessor

    def write_csv_files(self) -> None:
        if self.peloton_processor.new_workouts:
            self.pivots.year_table.to_csv(f"{const.PELOTON_CSV_DIR}/year_table.csv")
            self.pivots.month_table.to_csv(f"{const.PELOTON_CSV_DIR}/month_table.csv")
            self.pivots.totals_table.to_csv(f"{const.PELOTON_CSV_DIR}/totals_table.csv")
            self.peloton_processor.df_processed.to_csv(f"{const.PELOTON_CSV_DIR}/all_data.csv")

def check_for_peloton_processor(peloton_processor: PelotonProcessor):
    try:
        val = peloton_processor
    except UnboundLocalError:
        return None
    else:
        return val

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', dest='CHECK_FOR_NEW_WORKOUTS', action='store_const',
                        const=False, default=True,
                        help='do not check for new workouts on remote Peloton database')
    args = parser.parse_args()

    sql_engine = helpers.create_mariadb_engine(database=DATABASE)
    # sql_engine = db.create_engine(SQLITE_FILENAME)

    if args.CHECK_FOR_NEW_WORKOUTS:
        peloton_processor = PelotonProcessor(sql_engine)
        peloton_processor.pull_from_peloton_and_write_to_sql()

    # Whether or not there are new workouts, pull the full processed dataset from MariaDB and print to terminal
    df_processed_workouts_data_in_sql = helpers.ingest_processed_data_from_sql(sql_engine)
    df_processed_workouts_data_in_sql['start_time_strf'] = [datetime.fromisoformat(x).strftime('%a %h %d %I:%M %p') 
                                                            for x in df_processed_workouts_data_in_sql['start_time_iso'].tolist()]
    print(df_processed_workouts_data_in_sql[['start_time_strf', 'ride_title', 'instructor_name', 'total_output', 
                                             'distance', 'calories', 'heart_rate_avg', 'strive_score']].tail(15))

    # Print pivot tables
    pivots = PelotonPivots(df_processed_workouts_data_in_sql)
    pivots.print_pivot_tables()

    # If there are new workouts, write pivot tables to CSV
    try:
        if peloton_processor is not None:
            pivot_csv_writer = PivotCSVWriter(pivots, peloton_processor)
            pivot_csv_writer.write_csv_files()
    except UnboundLocalError:
        pass
    
    
    

       
if __name__ == "__main__":
    main()