import ast
import json

import pandas as pd
import pylotoncycle
import sqlalchemy as db

import peloton.functions as rdt
from peloton.peloton_ride import PelotonRide, PelotonRideGroup
from peloton.constants import PELOTON_PASSWORD, PELOTON_USERNAME
from peloton.helpers import create_mariadb_engine

    # df_metrics_raw = rdt.ingest_raw_metrics_data_from_sql(SQL_ENGINE_TEST)
    # df_processed = rdt.ingest_processed_data_from_sql(SQL_ENGINE_TEST)    
    # df_workouts_raw = rdt.ingest_raw_workout_data_from_sql(SQL_ENGINE_TEST)


def copy_tables_to_testing_database():
    engine_main = create_mariadb_engine("peloton")
    engine_test = create_mariadb_engine("peloton_test")

    with engine_main.connect() as conn:
        df_workouts_raw = pd.read_sql("SELECT * from raw_data_workouts", conn)
        df_metrics_raw  = pd.read_sql("SELECT * from raw_data_metrics", conn)
        df_processed = pd.read_sql("SELECT * from peloton", conn)

    with engine_test.connect() as conn:
        df_workouts_raw.to_sql("raw_data_workouts", conn, if_exists="replace", index=False)
        df_metrics_raw.to_sql("raw_data_metrics", conn, if_exists="replace", index=False)
        df_processed.to_sql("peloton", conn, if_exists="replace", index=False)


def copy_df_to_new_table_in_testing_database(input_df: pd.DataFrame, table: str, convert_dtypes: bool = False):
    if convert_dtypes:
        # Convert all datatypes (other than int64/float64/bool) to strings
        for column in input_df.select_dtypes(exclude=['int64', 'float64', 'bool']).columns:
            input_df[column] = input_df[column].astype("string")
        
    engine_test = create_mariadb_engine("peloton_test")
    with engine_test.connect() as conn:
        input_df.to_sql(table, conn, if_exists="replace", index=False)
        

def get_full_list_of_workout_ids_from_peloton(py_conn, num_workouts, limit: int = 25):
    workouts_list = py_conn.GetRecentWorkouts()
    workout_ids_list = [w["id"] for w in workouts_list]
    workout_ids_df = pd.DataFrame(workout_ids_list)
    workout_ids_df.to_csv("workout_ids.csv")

def generate_ride_df(df_workouts_raw: pd.DataFrame) -> pd.DataFrame:
    ride_series = df_workouts_raw['ride']
    ride_list_of_dicts = [ast.literal_eval(value) for index, value in ride_series.items()]

    print(len(ride_list_of_dicts))
    print(len(df_workouts_raw['workout_id'].tolist()))

    for i, x in enumerate(ride_list_of_dicts):
        x.update({'workout_id': df_workouts_raw['workout_id'][i]})

    ride_df = pd.json_normalize(ride_list_of_dicts)
    return ride_df


def generate_splits_data_df(df_workouts_raw: pd.DataFrame, df_metrics_raw: pd.DataFrame) -> pd.DataFrame:
    splits_data_series = df_metrics_raw['splits_data']
    # splits_list_of_dicts = []
    
    # # for index, value in splits_data_series.items():
    # #     dict = ast.literal_eval(value)
    # #     if 'splits' in dict.keys():
    # #         splits_list_of_dicts.append(dict)
    # #     else:
    # #         print("NO")

    ############# This one is hard because it's a two-dimensional thing:  once you get each "splits" table, you'll
    ############# need to make a DataFrame with a MultiIndex -- like this:
    ############# ID1 0 DATA
    ############# ID1 1 DATA
    ############# ID1 2 DATA
    ############# ID2 0 DATA
    ############# ID2 1 DATA
    ############# ID2 2 DATA
    
    splits_data_list_of_dicts = [ast.literal_eval(value[index]) if 'splits' in ast.literal_eval(value).keys() else {} for index, value in splits_data_series.items() ]

    print(pd.json_normalize(splits_data_list_of_dicts[2]['splits']))
    if len(splits_data_list_of_dicts) != len(df_workouts_raw['workout_id'].tolist()):
        print("ERROR: Number of Workout IDs does not equal number of workouts in dataset")
        return None
    
    for i, x in enumerate(splits_data_list_of_dicts):
        x.update({'workout_id': df_workouts_raw['workout_id'][i]})

    return pd.json_normalize(splits_data_list_of_dicts)


def main():
    py_conn = pylotoncycle.PylotonCycle(PELOTON_USERNAME, PELOTON_PASSWORD)
    SQL_ENGINE_TEST = create_mariadb_engine("peloton_test")

    df_workouts_raw = rdt.ingest_raw_workout_data_from_sql(SQL_ENGINE_TEST)
    df_metrics_raw = rdt.ingest_raw_metrics_data_from_sql(SQL_ENGINE_TEST)
    # df_processed = rdt.ingest_processed_data_from_sql(SQL_ENGINE_TEST)  

    splits_data_df = generate_splits_data_df(df_workouts_raw, df_metrics_raw)
    # print(splits_data_df.columns)
    splits_data_df.to_csv("splits_test2.csv")
    # copy_df_to_new_table_in_testing_database(ride_df, "raw_data_ride", convert_dtypes=True)



#### OTHER SUBTABLES FROM "WORKOUTS":
# - "total_heart_rate_zone_durations" - can probably skip
# - "achievement_templates" - only filled when there's an achievement; empty otherwise
# - "overall_summary"

#### OTHER SUBTABLES FROM "METRICS":
# - "segment_list" - can probably skip; just lists data for "warmup," "cooldown," etc.
# - "seconds_since_pedaling_start" - can probably skip
# - "splits_data"
# - "splits_metrics"
# - "target_performance_metrics"
# - "target_metrics_performance_data"
# - "muscle_group_score"

#### SUBTABLES FROM METRICS - ALREADY PROCSSED IN MAIN FUNCTION:
# - "average_summaries"
# - "summaries"
# - "metrics" 
# - "effort_zones"

################## CODE FOR GENERATING & EXPORTING "RIDE" TABLE ##############################    
    # ride_df = generate_ride_df(df_workouts_raw)
    # print(ride_df)
    # copy_df_to_new_table_in_testing_database(ride_df, "raw_data_ride", convert_dtypes=True)
    


if __name__ == "__main__":
    main()