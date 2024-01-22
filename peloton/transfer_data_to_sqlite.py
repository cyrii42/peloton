import pandas as pd
import sqlalchemy as db

import peloton.constants as const
import peloton.functions as func
import peloton.helpers as helpers

DATABASE = const.MARIADB_DATABASE


def main():
    sql_engine = helpers.create_mariadb_engine(database=DATABASE)
    sqlite_engine = db.create_engine("sqlite://../data/peloton.db")

    df_raw_workouts_data_in_sql = func.ingest_raw_workout_data_from_sql(sql_engine)
    func.export_raw_workout_data_to_sql(df_raw_workouts_data_in_sql, sqlite_engine)

    df_raw_metrics_data_in_sql = func.ingest_raw_metrics_data_from_sql(sql_engine)
    func.export_raw_metrics_data_to_sql(df_raw_metrics_data_in_sql, sqlite_engine)

    df_processed_workouts_data_in_sql = func.ingest_processed_data_from_sql(sql_engine)
    func.export_processed_data_to_sql(df_processed_workouts_data_in_sql, sqlite_engine)

    

       
if __name__ == "__main__":
    main()
