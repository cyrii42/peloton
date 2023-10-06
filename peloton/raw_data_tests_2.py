import ast
import json

import pandas as pd
import pylotoncycle
import sqlalchemy as db

import peloton.raw_data_tests as rdt
from peloton.classes import PelotonRide, PelotonRideGroup
from peloton.constants import MARIADB_DATABASE as SQL_DB
from peloton.constants import PELOTON_PASSWORD, PELOTON_USERNAME
from peloton.copy_tables_to_test_db import (
    copy_df_to_new_table_in_testing_database, copy_tables_to_testing_database)
from peloton.helpers import create_mariadb_engine

SQL_ENGINE_TEST_DB = create_mariadb_engine("peloton_test")


# df_workouts_raw = rdt.ingest_raw_workout_data_from_sql(SQL_ENGINE_TEST_DB)
# df_metrics_raw  = rdt.ingest_raw_metrics_data_from_sql(SQL_ENGINE_TEST_DB)
# df_processed = rdt.ingest_processed_data_from_sql(SQL_ENGINE_TEST_DB)


def generate_ride_df(df_workouts_raw: pd.DataFrame) -> pd.DataFrame:
    df_workouts_raw = rdt.ingest_raw_workout_data_from_sql(SQL_ENGINE_TEST_DB)
    ride_series = df_workouts_raw['ride']
    ride_list_of_dicts = [ast.literal_eval(value) for index, value in ride_series.items()]

    print(len(ride_list_of_dicts))
    print(len(df_workouts_raw['workout_id'].tolist()))

    for i, x in enumerate(ride_list_of_dicts):
        x.update({'workout_id': df_workouts_raw['workout_id'][i]})

    ride_df = pd.json_normalize(ride_list_of_dicts)
    return ride_df


def main():
    df_workouts_raw = rdt.ingest_raw_workout_data_from_sql(SQL_ENGINE_TEST_DB)
    ride_df = generate_ride_df(df_workouts_raw)
    print(ride_df)
    copy_df_to_new_table_in_testing_database(ride_df, "raw_data_ride", convert_dtypes=True)
    


if __name__ == "__main__":
    main()