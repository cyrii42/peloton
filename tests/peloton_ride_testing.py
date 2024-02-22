import ast
from pprint import pprint

import pandas as pd
import sqlalchemy as db
from pylotoncycle import PylotonCycle

import peloton.constants as const
from peloton.helpers import create_mariadb_engine
from peloton.schema.peloton_ride import PelotonRide, PelotonRideGroup

DATABASE = const.MARIADB_DATABASE
TEST_ID = '7c32268e13784898aa617d4a610edfb6'

def ingest_raw_workout_data_from_sql(sql_engine: db.Engine) -> pd.DataFrame:
    with sql_engine.connect() as conn:
        df = pd.read_sql("SELECT * from raw_data_workouts", conn)
    return df


def ingest_raw_metrics_data_from_sql(sql_engine: db.Engine) -> pd.DataFrame:
    with sql_engine.connect() as conn:
        df = pd.read_sql("SELECT * from raw_data_metrics", conn)
    return df


def process_workouts_from_raw_data(self) -> pd.DataFrame:
    df_workouts = self.df_raw_workout_data_new.set_index("id")
    df_workout_metrics = self.df_raw_workout_metrics_data_new.set_index("id")

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
    output_df = ride_group.create_dataframe()
    return output_df


def process_test(df_raw_workout_data_new: pd.DataFrame, df_raw_workout_metrics_data_new: pd.DataFrame) -> pd.DataFrame():
    df_workouts = df_raw_workout_data_new.set_index("id")
    df_workout_metrics = df_raw_workout_metrics_data_new.set_index("id")
    
    for row in df_workouts.itertuples():
        print(type(eval(row._asdict()['ride'])))
        print('')
    
    
    # py_conn = PylotonCycle(const.PELOTON_USERNAME, const.PELOTON_PASSWORD) 

    # workout = py_conn.GetWorkoutById(TEST_ID)
    # pprint(workout)

    # workout_summary = py_conn.GetWorkoutSummaryById(TEST_ID)
    # pprint(workout_summary)

    # workouts_from_peloton = py_conn.GetRecentWorkouts(2)

    # pprint(workouts_from_peloton[1])

    # workout_ids_list = [x for x in df_raw_workout_data_new['workout_id'].tolist()]
    # workout_metrics_list = [py_conn.GetWorkoutMetricsById(workout_id) for workout_id in workout_ids_list[:3]]

    # pprint(workout_metrics_list[0])


def main():
    sql_engine = create_mariadb_engine(DATABASE)
    df_raw_workout_data = ingest_raw_workout_data_from_sql(sql_engine)
    df_raw_workout_metrics_data = ingest_raw_metrics_data_from_sql(sql_engine)
    
    process_test(df_raw_workout_data, df_raw_workout_metrics_data)


if __name__ == '__main__':
    main()