import ast

import pandas as pd
from pylotoncycle import PylotonCycle

from peloton.models.peloton_ride import PelotonRide, PelotonRideGroup


def calculate_new_workouts_num(py_conn: PylotonCycle, df_raw_workouts_data_in_sql: pd.DataFrame) -> int:
    ''' Calculates the number of new workouts on the Peloton servers, doublechecks that number, and then returns it. '''
    
    total_workouts = py_conn.GetMe()["total_workouts"]
    existing_workouts = df_raw_workouts_data_in_sql.shape[0]
    new_workouts = total_workouts - existing_workouts

    print(f"Total Workouts: {total_workouts}")
    print(f"Workouts in Database: {existing_workouts}")
    print(f"New Workouts to Write: {new_workouts}")

    workouts_from_peloton = pd.DataFrame(py_conn.GetRecentWorkouts(new_workouts + 1))  # returns a list of dicts
    workouts_from_peloton['workout_id'] = [x for x in workouts_from_peloton['id'].tolist()]
    workout_ids_from_peloton = workouts_from_peloton['workout_id']
    last_non_new_workout_on_peloton = workout_ids_from_peloton.iloc[-1]
    print(f"Last non-new workout on Peloton: {workout_ids_from_peloton.iloc[-1]}")

    df_raw_workouts_data_in_sql = df_raw_workouts_data_in_sql.sort_values(by=['start_time'])
    workout_ids_from_sql = df_raw_workouts_data_in_sql['workout_id']
    last_workout_id_from_sql = workout_ids_from_sql.iloc[-1]
    print(f"Last workout on SQL: {workout_ids_from_sql.iloc[-1]}")

    workout_ids_check_bool = last_non_new_workout_on_peloton == last_workout_id_from_sql
    print(f"Are they the same?  {workout_ids_check_bool}")

    if workout_ids_check_bool:
        return new_workouts
    else:
        print("There was a problem with data ingestion: workout IDs did not match.")
        print("Peloton Workout IDs:\n")
        print(workout_ids_from_peloton)
        print("SQL Workout IDs:\n")
        print(workout_ids_from_sql)
        exit()


def pull_new_raw_workouts_data_from_peloton(py_conn: PylotonCycle, new_workouts: int) -> pd.DataFrame:
    """ Pulls the raw workout data from Peloton for the corresponding number of workouts. """
    
    return pd.DataFrame(py_conn.GetRecentWorkouts(new_workouts))
        

def pull_new_raw_metrics_data_from_peloton(py_conn: PylotonCycle, workouts_df: pd.DataFrame) -> pd.DataFrame:
    workout_ids_list = [x for x in workouts_df['workout_id'].tolist()]
    workout_metrics_list = [py_conn.GetWorkoutMetricsById(workout_id) for workout_id in workout_ids_list]
    workout_metrics_df = pd.DataFrame(workout_metrics_list)
    workout_metrics_df["id"] = [x for x in workout_ids_list]
    workout_metrics_df["workout_id"] = [x for x in workout_ids_list]

    return workout_metrics_df


def REFACTORED_process_workouts_from_raw_data(df_workouts: pd.DataFrame, df_workout_metrics: pd.DataFrame) -> pd.DataFrame:
    df_workouts = df_workouts.set_index("id")
    df_workout_metrics = df_workout_metrics.set_index("id")

    #  

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


def main():
    print("This is a module, not a script.")
    exit()


if __name__ == "__main__":
    main()
