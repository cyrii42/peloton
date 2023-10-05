import sqlalchemy as db
import pandas as pd
import pylotoncycle
from datetime import datetime
import constants as const
from classes import PelotonRide, PelotonRideGroup
from helpers import create_mariadb_engine, jprint

import csv
import json
import random


def get_total_workouts_num(py_conn: pylotoncycle.PylotonCycle) -> int:
    return py_conn.GetMe()["total_workouts"]


def pull_new_raw_workout_data_from_peloton(py_conn: pylotoncycle.PylotonCycle, workouts_num: int) -> pd.DataFrame:
    # filename_out = str(datetime.now().strftime("%Y-%m-%d_%H-%M")) + "_peloton_raw_data.csv"
    
    workouts_list = py_conn.GetRecentWorkouts(workouts_num)  ## defaults to all workouts if nothing passed
    workouts_df = pd.DataFrame(workouts_list)
    
    workout_ids_list = [w['id'] for w in workouts_list]
    workout_metrics_list = [py_conn.GetWorkoutMetricsById(workout_id) for workout_id in workout_ids_list]
    workout_metrics_df = pd.DataFrame(workout_metrics_list)
    
    combined_df = pd.concat([workouts_df, workout_metrics_df], axis='columns')
    
    return combined_df



def pull_all_raw_workout_data_from_peloton(py_conn: pylotoncycle.PylotonCycle, workouts_num: int) -> pd.DataFrame:  
    workouts_list = py_conn.GetRecentWorkouts(workouts_num)  ## defaults to all workouts if nothing passed
    workouts_df = pd.DataFrame(workouts_list)
    
    return workouts_df



def combine_workout_dataframes(df1: pd.DataFrame, df2: pd.DataFrame) -> pd.DataFrame:
    return pd.concat([df1, df2], axis='columns')


def pull_all_raw_metrics_data_from_peloton(py_conn: pylotoncycle.PylotonCycle, workout_ids_list_of_lists: list[list[str]]) -> pd.DataFrame:
    workout_ids_list_part_one = workout_ids_list_of_lists[0]
    workout_metrics_list_part_one = [py_conn.GetWorkoutMetricsById(workout_id) for workout_id in workout_ids_list_part_one]
    
    workout_metrics_df = pd.DataFrame(workout_metrics_list_part_one)
    
    num_groups = len(workout_ids_list_of_lists)
    print(f"Number of groups:  {num_groups}")
    
    for x in range(num_groups):
        if x == 0:
            print("Skipped range 0.")
            continue
        else:
            workout_ids_list_part_x = workout_ids_list_of_lists[x]
            workout_metrics_list_part_x = [py_conn.GetWorkoutMetricsById(workout_id) for workout_id in workout_ids_list_part_x]
            print(f"Pulled new partial list of workout metrics, which has {len(workout_metrics_list_part_x)} entries.")
            workout_metrics_df_part_x = pd.DataFrame(workout_metrics_list_part_x)
            print(f"Created partial workout_metrics_df with {workout_metrics_df_part_x.shape[0]} entries")
            workout_metrics_df = pd.concat([workout_metrics_df, workout_metrics_df_part_x], ignore_index=True)
            print(f"Added to main workout_metrics_df, which now has {workout_metrics_df.shape[0]} entries")
                                 
    return workout_metrics_df
        

def calculate_new_workouts_num(py_conn: pylotoncycle.PylotonCycle, df_input: pd.DataFrame) -> int:
    total_workouts = py_conn.GetMe()["total_workouts"]
    existing_workouts = df_input.shape[0]
    new_workouts = total_workouts - existing_workouts

    print(f"Total Workouts: {total_workouts}")
    print(f"Workouts in Database: {existing_workouts}")
    print(f"New Workouts to Write: {new_workouts}")
    
    return new_workouts


def export_raw_data_to_sql(input_df: pd.DataFrame, engine: db.Engine):
     with engine.connect() as conn:
        input_df.to_sql("raw_data", conn, if_exists="append", index=False)


def get_full_list_of_workout_ids_from_pyloton(py_conn, num_workouts, limit: int = 25):
    workouts_list = py_conn.GetRecentWorkouts()
    workout_ids_list = [w['id'] for w in workouts_list]
    workout_ids_df = pd.DataFrame(workout_ids_list)
    workout_ids_df.to_csv("workout_ids.csv")


def get_full_list_of_workout_ids_from_csv(filename: str) -> list[str]:
    workout_ids_df = pd.read_csv(filename, index_col=0)
    return workout_ids_df['0'].values.tolist()
    

def split_workout_ids_into_groups(workout_ids_list: list[str], limit: int = 25) -> list[list[str]]:
    limit = limit
    num_workouts = len(workout_ids_list)
    num_groups = num_workouts // limit
    remainder = num_workouts % limit
    
    list_of_lists = []
    for x in range(num_groups):
        group_range_start = x * limit
        group_range_end = group_range_start + limit
        list_part = [workout_ids_list[x] for x in range(group_range_start, group_range_end)]
        print(f"Created list part with {len(list_part)} entries.")
        list_of_lists.append(list_part)
        
    if remainder > 0:
        remainder_start = num_workouts - remainder
        remainder_end = num_workouts
        list_remainder = [workout_ids_list[x] for x in range(remainder_start, remainder_end)]
        list_of_lists.append(list_remainder)
    
    # print(f"List of lists is {len(list_of_lists)} lists long.")
    # print(pd.DataFrame(list_of_lists))
    
    return list_of_lists



def main():
    # SQL_DB = "peloton"

    py_conn = pylotoncycle.PylotonCycle(const.PELOTON_USERNAME, const.PELOTON_PASSWORD) 
    # sql_conn = create_mariadb_engine(database=SQL_DB)
    
    # pull_raw_workout_data_from_peloton(py_conn, 2)
    
    # print(get_total_workouts_num(py_conn))
    
    # random_str_list = [random.randint(100000, 999999) for x in range(170)]
    # split_workout_ids_into_groups(random_str_list)
    
    # get_full_list_of_workout_ids(py_conn, 170)
    
    # get_full_list_of_workout_ids_from_csv("workout_ids.csv")
    

    
    # workout_ids_list = get_full_list_of_workout_ids_from_csv("workout_ids.csv")
    # workout_ids_list_of_lists = split_workout_ids_into_groups(workout_ids_list)
    
    # filename_out_workouts = str(datetime.now().strftime("%Y-%m-%d_%H-%M")) + "_peloton_raw_data_workouts.csv"
    # workouts_df = pull_all_raw_workout_data_from_peloton(py_conn, 170)
    # print(workouts_df)
    # workouts_df.to_csv(filename_out_workouts)
    
    # filename_out_metrics = str(datetime.now().strftime("%Y-%m-%d_%H-%M")) + "_peloton_raw_data_metrics.csv"
    # workout_metrics_df = pull_all_raw_metrics_data_from_peloton(py_conn, workout_ids_list_of_lists)
    # print(workout_metrics_df)
    # workout_metrics_df.to_csv(filename_out_metrics)
    
    # workouts_df = pd.read_csv("2023-10-04_22-16_peloton_raw_data_workouts.csv", index_col=0)
    # workout_metrics_df = pd.read_csv("2023-10-04_22-34_peloton_raw_data_metrics.csv", index_col=0)
    
    # df_combined = combine_workout_dataframes(workouts_df, workout_metrics_df)
    
    # print(df_combined)
    
    # filename_out_combined = str(datetime.now().strftime("%Y-%m-%d_%H-%M")) + "_peloton_raw_data_combined.csv"
    
    # df_combined.to_csv(filename_out_combined)
    
    
    existing_workouts_test = pd.read_csv("peloton_raw_data_combined.csv", index_col=0)
    
    new_workouts_num = calculate_new_workouts_num(py_conn, existing_workouts_test)
    
    new_combined_df = pull_new_raw_workout_data_from_peloton(py_conn, new_workouts_num)
    
    print(new_combined_df)
    

    
    
    
        
        
if __name__ == "__main__":
    main()