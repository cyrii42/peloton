import pandas as pd
import pylotoncycle

from peloton.helpers import create_mariadb_engine

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
    print("This is a module, not a script.")
    exit()


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
