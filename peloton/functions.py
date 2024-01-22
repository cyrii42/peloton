import ast

import pandas as pd
import pylotoncycle
import sqlalchemy as db

from peloton.classes import PelotonRide, PelotonRideGroup
from peloton.constants import MARIADB_DATABASE as SQL_DB
from peloton.constants import PELOTON_PASSWORD, PELOTON_USERNAME
from peloton.helpers import create_mariadb_engine


def calculate_new_workouts_num(py_conn: pylotoncycle.PylotonCycle, df_input: pd.DataFrame) -> int:
    total_workouts = py_conn.GetMe()["total_workouts"]
    existing_workouts = df_input.shape[0]
    new_workouts = total_workouts - existing_workouts

    print(f"Total Workouts: {total_workouts}")
    print(f"Workouts in Database: {existing_workouts}")
    print(f"New Workouts to Write: {new_workouts}")

    return new_workouts 


def pull_new_raw_data_from_peloton(py_conn: pylotoncycle.PylotonCycle, workouts_num: int) -> (pd.DataFrame, pd.DataFrame):
    workouts_list = py_conn.GetRecentWorkouts(workouts_num)  ## defaults to all workouts if nothing passed
    workouts_df = pd.DataFrame(workouts_list)
    workouts_df["workout_id"] = [x for x in workouts_df['id'].tolist()]

    workout_ids_list = [w["id"] for w in workouts_list]
    workout_metrics_list = [py_conn.GetWorkoutMetricsById(workout_id) for workout_id in workout_ids_list]
    workout_metrics_df = pd.DataFrame(workout_metrics_list)
    workout_metrics_df["id"] = [x for x in workout_ids_list]
    workout_metrics_df["workout_id"] = [x for x in workout_ids_list]

    return (workouts_df, workout_metrics_df)


def pull_new_raw_workouts_data_from_peloton(py_conn: pylotoncycle.PylotonCycle, df_raw_workouts_data_in_sql: pd.DataFrame, new_workouts: int) -> pd.DataFrame:
    """ NOT YET FULLY IMPLEMENTED: a function for double-checking the count returned by calculate_new_workouts_num() """
    
    workouts_from_peloton = pd.DataFrame(py_conn.GetRecentWorkouts(new_workouts + 1))
    workouts_from_peloton['workout_id'] = [x for x in workouts_from_peloton['id'].tolist()]
    workout_ids_from_peloton = workouts_from_peloton['workout_id']
    last_non_new_workout_on_peloton = workout_ids_from_peloton.iloc[-1]
    print(f"Last non-new workout on Peloton: {workout_ids_from_peloton.iloc[-1]}")  # "-1" gets the final entry; the list is in reverse-chron, so the last row is the least recent

    df_raw_workouts_data_in_sql = df_raw_workouts_data_in_sql.sort_values(by=['start_time'])
    workout_ids_from_sql = df_raw_workouts_data_in_sql['workout_id']
    last_workout_id_from_sql = workout_ids_from_sql.iloc[-1]
    print(f"Last workout on SQL: {workout_ids_from_sql.iloc[-1]}")

    workout_ids_check_bool = last_non_new_workout_on_peloton == last_workout_id_from_sql
    print(f"Are they the same?  {workout_ids_check_bool}")

    if last_non_new_workout_on_peloton == last_workout_id_from_sql:
        df_scrubbed = workouts_from_peloton.drop(index=workouts_from_peloton.index[-1])
        return df_scrubbed
    else:
        print("There was a problem with data ingestion: workout IDs did not match.")
        print("Peloton Workout IDs:\n")
        print(workout_ids_from_peloton)
        print("SQL Workout IDs:\n")
        print(workout_ids_from_sql)
        exit()
        

def pull_new_raw_metrics_data_from_peloton(py_conn: pylotoncycle.PylotonCycle, workouts_df: pd.DataFrame) -> pd.DataFrame:
    workout_ids_list = [x for x in workouts_df['workout_id'].tolist()]
    workout_metrics_list = [py_conn.GetWorkoutMetricsById(workout_id) for workout_id in workout_ids_list]
    workout_metrics_df = pd.DataFrame(workout_metrics_list)
    workout_metrics_df["id"] = [x for x in workout_ids_list]
    workout_metrics_df["workout_id"] = [x for x in workout_ids_list]

    return workout_metrics_df


def combine_workout_dataframes(df1: pd.DataFrame, df2: pd.DataFrame) -> pd.DataFrame:
    return pd.concat([df1, df2], axis="columns")


def export_raw_workout_data_to_sql(input_df: pd.DataFrame, engine: db.Engine):
    # Convert all datatypes (other than int64/float64) to strings for subsequent SQL export
    for column in input_df.select_dtypes(exclude=['int64', 'float64', 'bool']).columns:
        input_df[column] = input_df[column].astype("string")

    with engine.connect() as conn:
        input_df.to_sql("raw_data_workouts", conn, if_exists="append", index=False)


def export_raw_metrics_data_to_sql(input_df: pd.DataFrame, engine: db.Engine):
    # Convert all datatypes (other than int64/float64) to strings for subsequent SQL export
    for column in input_df.select_dtypes(exclude=['int64', 'float64', 'bool']).columns:
        input_df[column] = input_df[column].astype("string")
        
    with engine.connect() as conn:
        input_df.to_sql("raw_data_metrics", conn, if_exists="append", index=False)


def export_processed_data_to_sql(input_df: pd.DataFrame, engine: db.Engine):
    with engine.connect() as conn:
        input_df.to_sql("peloton", conn, if_exists="append", index=False)


def ingest_raw_workout_data_from_sql(engine: db.Engine) -> pd.DataFrame:
    with engine.connect() as conn:
        df = pd.read_sql("SELECT * from raw_data_workouts", conn)
    return df


def ingest_raw_metrics_data_from_sql(engine: db.Engine) -> pd.DataFrame:
    with engine.connect() as conn:
        df = pd.read_sql("SELECT * from raw_data_metrics", conn)
    return df


def ingest_processed_data_from_sql(engine: db.Engine) -> pd.DataFrame:
    with engine.connect() as conn:
        df = pd.read_sql("SELECT * from peloton", conn)
    return df


def process_workouts_from_raw_data(df_workouts: pd.DataFrame, df_workout_metrics: pd.DataFrame) -> pd.DataFrame:
    df_workouts = df_workouts.set_index("id")
    df_workout_metrics = df_workout_metrics.set_index("id")

    ride_group_list = []

    for index, workout_series in df_workouts.iterrows():
        df_workout_ride = pd.json_normalize(ast.literal_eval(workout_series["ride"]))
        workout_id = workout_series['workout_id']
        ride_attributes_dict = {}
        # workout_id = index
        # ride_attributes_dict = {"workout_id": workout_id}

        # Loop through the regular columns in df_workout and then the "ride" columns
        ride_attributes_dict.update({ label: data for label, data in workout_series.items() })
        ride_attributes_dict.update({ f"ride_{column}": df_workout_ride[column][0] for column in df_workout_ride.columns })

        # Pull the corresponding row of the Metrics DataFrame and put it into a Series
        workout_metrics_series = df_workout_metrics.loc[workout_id] 

        # Loop through summaries (total_output, distance, calories)
        df_summaries = pd.json_normalize(ast.literal_eval(workout_metrics_series["summaries"]))
        ride_attributes_dict.update({ df_summaries["slug"][index]: df_summaries["value"][index] for index, row in df_summaries.iterrows() })

        # Loop through average & max values (output, cadence, resistance, speed, HR)
        df_metrics = pd.json_normalize(ast.literal_eval(workout_metrics_series["metrics"]))
        df_average_values = df_metrics.set_index("slug")["average_value"]
        df_max_values = df_metrics.set_index("slug")["max_value"]
        ride_attributes_dict.update({ f"{index}_avg": value for index, value in df_average_values.items() })
        ride_attributes_dict.update({ f"{index}_max": value for index, value in df_max_values.items() })

        # Set "Strive Score" attribute & loop through HR Zone Duration columns
        if workout_metrics_series.notna()["effort_zones"]:
            df_effort_zones = pd.json_normalize(ast.literal_eval(workout_metrics_series["effort_zones"]))

            ride_attributes_dict.update({ "strive_score": df_effort_zones["total_effort_points"][0] })
            for x in range(4):
                zone_num = x + 1
                column_name = f"heart_rate_zone_durations.heart_rate_z{zone_num}_duration"
                ride_attributes_dict.update({ column_name: df_effort_zones[column_name][0] })

        # Create the PelotonRide object from the "ride_attributes_dict" dictionary you just created
        ride_object = PelotonRide.from_dict(ride_attributes_dict)

        # Add newly created ride object to the running list (which will be used after the loop to make a PelotonRideGroup object)
        ride_group_list.append(ride_object)
        print(f"Pulled and processed {ride_object.start_time_iso}")

    # After the loop, create a PelotonRideGroup object from the list of PelotonRide objects
    ride_group = PelotonRideGroup(ride_group_list)

    # Return a DataFrame of the Peloton rides using the create_dataframe() method in the PelotonRideGroup object
    return ride_group.create_dataframe()


#####################################################################################
############## SPECIALIZED FUNCTIONS FOR FIRST PULL OF ALL PELOTON DATA #############
#####################################################################################


def delete_sql_raw_tables_and_replace_with_csv_data(workouts_csv: str, metrics_csv: str):
    engine = create_mariadb_engine(database="peloton")
    df_workouts = pd.read_csv(workouts_csv, index_col=0)
    df_workout_metrics = pd.read_csv(metrics_csv, index_col=0)

    with engine.connect() as conn:
        df_workouts.to_sql("raw_data_workouts", conn, if_exists="replace", index=False)
        df_workout_metrics.to_sql("raw_data_metrics", conn, if_exists="replace", index=False)


def get_total_workouts_num(py_conn: pylotoncycle.PylotonCycle) -> int:
    return py_conn.GetMe()["total_workouts"]


def get_full_list_of_workout_ids_from_peloton(py_conn, num_workouts, limit: int = 25):
    workouts_list = py_conn.GetRecentWorkouts()
    workout_ids_list = [w["id"] for w in workouts_list]
    workout_ids_df = pd.DataFrame(workout_ids_list)
    workout_ids_df.to_csv("workout_ids.csv")


def get_full_list_of_workout_ids_from_csv(filename: str) -> list[str]:
    workout_ids_df = pd.read_csv(filename, index_col=0)
    return workout_ids_df["0"].values.tolist()


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

    return list_of_lists


def pull_all_raw_workout_data_from_peloton(py_conn: pylotoncycle.PylotonCycle, workouts_num: int) -> pd.DataFrame:
    workouts_list = py_conn.GetRecentWorkouts(workouts_num)
    workouts_df = pd.DataFrame(workouts_list)

    return workouts_df


def pull_all_raw_metrics_data_from_peloton(py_conn: pylotoncycle.PylotonCycle, workout_ids_list_of_lists: list[list[str]]) -> pd.DataFrame:
    workout_ids_list_part_one = workout_ids_list_of_lists[0]
    workout_metrics_list_part_one = [py_conn.GetWorkoutMetricsById(workout_id) for workout_id in workout_ids_list_part_one]

    workout_metrics_df = pd.DataFrame(workout_metrics_list_part_one)
    workout_metrics_df["id"] = [x for x in workout_ids_list_part_one]

    num_groups = len(workout_ids_list_of_lists)
    print(f"Number of groups:  {num_groups}")

    for x in range(num_groups):
        if x == 0:
            continue
        else:
            workout_ids_list_part_x = workout_ids_list_of_lists[x]

            workout_metrics_list_part_x = [py_conn.GetWorkoutMetricsById(workout_id) for workout_id in workout_ids_list_part_x]
            print(f"Pulled new partial list of workout metrics, which has {len(workout_metrics_list_part_x)} entries.")

            workout_metrics_df_part_x = pd.DataFrame(workout_metrics_list_part_x)
            workout_metrics_df_part_x["id"] = [x for x in workout_ids_list_part_x]

            workout_metrics_df = pd.concat([workout_metrics_df, workout_metrics_df_part_x], ignore_index=True)
            print(f"Added to main workout_metrics_df, which now has {workout_metrics_df.shape[0]} entries")

    return workout_metrics_df




def main():
 
    py_conn = pylotoncycle.PylotonCycle(PELOTON_USERNAME, PELOTON_PASSWORD)
    sql_engine = create_mariadb_engine(database=SQL_DB)

    df_processed_data_in_sql = ingest_processed_data_from_sql(sql_engine)
    df_raw_workouts_data_in_sql = ingest_raw_workout_data_from_sql(sql_engine)
    df_raw_metrics_data_in_sql = ingest_raw_metrics_data_from_sql(sql_engine)

    new_workouts_num = calculate_new_workouts_num(py_conn, df_raw_workouts_data_in_sql)
    if new_workouts_num > 0:
        (df_raw_workout_data_new, df_raw_workout_metrics_data_new) = pull_new_raw_data_from_peloton(py_conn, new_workouts_num)

        # Write the new raw data to MariaDB
        export_raw_workout_data_to_sql(df_raw_workout_data_new, sql_engine)
        export_raw_metrics_data_to_sql(df_raw_workout_metrics_data_new, sql_engine)

        df_processed = process_workouts_from_raw_data(df_raw_workout_data_new, df_raw_workout_metrics_data_new)

        # Write the new processed data to MariaDB
        export_processed_data_to_sql(df_processed, sql_engine)

        print(df_processed)
    else:
        print(df_processed_data_in_sql)


    # ########## TO WRITE/REPLACE RAW DATA TO MARIA DB FOR ALL 170 WORKOKUTS ######################
    # delete_sql_raw_tables_and_replace_with_csv_data(
    #     workouts_csv="/home/zvaughan/python/peloton/2023-10-04_22-16_peloton_raw_data_workouts.csv",
    #     metrics_csv="/home/zvaughan/python/peloton/2023-10-05_11-25_peloton_raw_data_metrics.csv"
    #     )
    # #############################################################################################

    # ######## TO WRITE/REPLACE RAW DATA FOR 165 of 170 WORKOUTS #################################
    # delete_sql_raw_tables_and_replace_with_csv_data(
    #     workouts_csv="/home/zvaughan/python/peloton/2023-10-04_22-16_peloton_raw_data_workouts_minus5.csv",
    #     metrics_csv="/home/zvaughan/python/peloton/2023-10-05_11-25_peloton_raw_data_metrics_minus5.csv"
    #     )
    # ############################################################################################

    
    # # ####################### MORE STUFF FOR A FIRST-TIME INITIALIZATION #########################
    # py_conn = pylotoncycle.PylotonCycle(PELOTON_USERNAME, PELOTON_PASSWORD)
    # sql_engine = create_mariadb_engine(database=SQL_DB)

    # try:
    #     df_processed_data_in_sql = ingest_processed_data_from_sql(sql_engine)
    # except db.exc.ProgrammingError:
    #     df_raw_workouts_data_in_sql = ingest_raw_workout_data_from_sql(sql_engine).reset_index()
    #     df_raw_metrics_data_in_sql = ingest_raw_metrics_data_from_sql(sql_engine).reset_index()

    #     df_processed = process_workouts_from_raw_sql_data(df_raw_workouts_data_in_sql, df_raw_metrics_data_in_sql)

    #     print(df_processed)
        
    #     # Write the new processed data to MariaDB
    #     export_processed_data_to_sql(df_processed, sql_engine)
    # ##############################################################################################



if __name__ == "__main__":
    main()
