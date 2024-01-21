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

DATABASE = const.MARIADB_DATABASE
SQLITE_FILENAME = "sqlite:///data/peloton.db"

def main():
    py_conn = pylotoncycle.PylotonCycle(const.PELOTON_USERNAME, const.PELOTON_PASSWORD) 
        
    # sql_engine = helpers.create_mariadb_engine(database=DATABASE)
    sql_engine = db.create_engine(SQLITE_FILENAME)

    # Pull raw workout data from MariaDB and use it to calculate the number of new Peloton workouts
    df_raw_workouts_data_in_sql = func.ingest_raw_workout_data_from_sql(sql_engine)
    new_workouts_num = func.calculate_new_workouts_num(py_conn, df_raw_workouts_data_in_sql)
    
    if new_workouts_num > 0:
        df_raw_workout_data_new = func.pull_new_raw_workouts_data_from_peloton(py_conn, df_raw_workouts_data_in_sql, new_workouts_num)

        df_raw_workout_metrics_data_new = func.pull_new_raw_metrics_data_from_peloton(py_conn, df_raw_workout_data_new)

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
    parser.add_argument('-c', '--check-new-workouts', dest='CHECK_FOR_NEW_WORKOUTS', action='store_const',
                        const=True, default=False,
                        help='check for new workouts on remote Peloton database')
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
    df_pivots = pivots.get_sql_data_for_pivots(sql_engine)  
    year_table = pivots.get_pivot_table_year(df_pivots)
    month_table = pivots.get_pivot_table_month(df_pivots)
    totals_table = pivots.get_grand_totals_table(year_table)
    
    print(f"\n                             GRAND TOTALS")
    print(f"{totals_table}")
    print(f"\n{year_table}")
    print(f"\n{month_table}")

    if new_workouts_num > 0:
        year_table.to_csv(f"./data/year_table.csv")
        month_table.to_csv(f"./data/month_table.csv")
        totals_table.to_csv(f"./data/totals_table.csv")
        df_processed_workouts_data_in_sql.to_csv(f"./data/all_data.csv")

       
if __name__ == "__main__":
    main()