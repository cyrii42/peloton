import sqlalchemy as db
import pandas as pd
import pylotoncycle
from classes import PelotonRide, PelotonRideGroup

def process_workouts(py_conn: pylotoncycle.PylotonCycle, workouts_num: int = None) -> pd.DataFrame:
    ride_group_list = []
    
    workouts = py_conn.GetRecentWorkouts(workouts_num)  ## defaults to all workouts if nothing passed

    for w in workouts:
        df_workout = pd.json_normalize(w)
        df_workout_ride = pd.json_normalize(w['ride'])
        workout_id = df_workout['id'].loc[0]
        ride_attributes_dict = {}
        
        # Loop through the regular columns in df_workout and then the "ride" columns
        ride_attributes_dict.update({column: df_workout[column][0] for column in df_workout.columns})
        ride_attributes_dict.update({f"ride_{column}": df_workout_ride[column][0] for column in df_workout_ride.columns})

        # Pull metrics from Peloton, copy into a dictionary, create DataFrames
        workout_metrics_by_id_dict = py_conn.GetWorkoutMetricsById(workout_id)
        
        # Loop through summaries (total_output, distance, calories)
        df_summaries = pd.json_normalize(workout_metrics_by_id_dict['summaries'])
        ride_attributes_dict.update({ df_summaries['slug'][index]: df_summaries['value'][index] for index, row in df_summaries.iterrows() })
                     
        # Loop through average & max values (output, cadence, resistance, speed, HR)
        df_metrics = pd.json_normalize(workout_metrics_by_id_dict['metrics'])
        df_average_values = df_metrics.set_index('slug')['average_value']
        df_max_values = df_metrics.set_index('slug')['max_value']
        ride_attributes_dict.update({ f"{index}_avg": value for index, value in df_average_values.items() })
        ride_attributes_dict.update({ f"{index}_max": value for index, value in df_max_values.items() })

        # Set "Strive Score" attribute & loop through HR Zone Duration columns        
        if 'effort_zones' in workout_metrics_by_id_dict.keys():
            df_effort_zones = pd.json_normalize(workout_metrics_by_id_dict['effort_zones'])
            df_hr_zone_durations = pd.json_normalize(workout_metrics_by_id_dict['effort_zones']['heart_rate_zone_durations'])

            ride_attributes_dict.update({ "strive_score": df_effort_zones['total_effort_points'][0] })
            ride_attributes_dict.update({ column: df_hr_zone_durations[column][0] for column in df_hr_zone_durations.columns })        

        # Create the PelotonRide object from the "ride_attributes_dict" dictionary you just created
        ride_object = PelotonRide.from_dict(ride_attributes_dict)

        # Add newly created ride object to the running list (which will be used after the loop to make a PelotonRideGroup object)
        ride_group_list.append(ride_object)
        print(f"Pulled and processed {ride_object.start_time_iso}")
                                 
    # After the loop, create a PelotonRideGroup object from the list of PelotonRide objects
    ride_group = PelotonRideGroup(ride_group_list)
    
    # Return a DataFrame of the Peloton rides using the create_dataframe() method in the PelotonRideGroup object
    return ride_group.create_dataframe()


def get_peloton_data_from_sql(engine: db.Engine) -> pd.DataFrame:
    with engine.connect() as conn:
        df = pd.read_sql(
            "SELECT * from peloton",
            conn,
            index_col='start_time_iso',
            parse_dates=['start_time_iso', 'start_time_local']
            )
    return df


def export_peloton_data_to_sql(input_df: pd.DataFrame, engine: db.Engine):
     with engine.connect() as conn:
        input_df.to_sql("peloton", conn, if_exists="append", index=False)
        
        
def select_all_from_table(engine: db.Engine, table: str, index_col: str = None, parse_dates: list[str] = None
                            ) -> pd.DataFrame:
    with engine.connect() as conn:
        df = pd.read_sql(
            f"SELECT * from {table}",
            conn,
            index_col=index_col,
            parse_dates=parse_dates
            )
    return df

# Calculate number of new workouts not yet in DB
def calculate_new_workouts_num(py_conn: pylotoncycle.PylotonCycle, df_input: pd.DataFrame) -> int:
    total_workouts = py_conn.GetMe()["total_workouts"]
    existing_workouts = df_input.shape[0]
    new_workouts = total_workouts - existing_workouts

    print(f"Total Workouts: {total_workouts}")
    print(f"Workouts in Database: {existing_workouts}")
    print(f"New Workouts to Write: {new_workouts}")
    
    return new_workouts