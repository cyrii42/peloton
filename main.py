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
    df_raw_workouts_data_in_sql = helpers.ingest_raw_workout_data_from_sql(sql_engine)
    new_workouts_num = func.calculate_new_workouts_num(py_conn, df_raw_workouts_data_in_sql)
    
    if new_workouts_num > 0:
        df_raw_workout_data_new = func.pull_new_raw_workouts_data_from_peloton(py_conn, df_raw_workouts_data_in_sql, new_workouts_num)

        df_raw_workout_metrics_data_new = func.pull_new_raw_metrics_data_from_peloton(py_conn, df_raw_workout_data_new)

        # Write the new raw data to MariaDB
        helpers.export_raw_workout_data_to_sql(df_raw_workout_data_new, sql_engine)
        helpers.export_raw_metrics_data_to_sql(df_raw_workout_metrics_data_new, sql_engine)
        
        # Process the new raw data
        df_processed = func.process_workouts_from_raw_data(df_raw_workout_data_new, df_raw_workout_metrics_data_new)

        # Write the new processed data to MariaDB
        helpers.export_processed_data_to_sql(df_processed, sql_engine)

    # Whether or not there are new workouts, pull the full processed dataset from MariaDB and print to terminal
    df_processed_workouts_data_in_sql = helpers.ingest_processed_data_from_sql(sql_engine)
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