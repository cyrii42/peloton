import ast
import sqlalchemy as db
from datetime import datetime

from pylotoncycle import PylotonCycle
import pandas as pd

import peloton.constants as const
from peloton.peloton_ride import PelotonRide, PelotonRideGroup

class PelotonProcessor():   
    ''' Object for pulling new data from Peloton, processing it, and exporting to SQL. '''
    
    def __init__(self, sql_engine: db.Engine):
        self.sql_engine = sql_engine
        self.new_workouts = False
        self.new_workouts_num = 0
        self.df_processed = self.ingest_processed_data_from_sql()


    def check_for_new_workouts(self) -> None:
        ''' Pulls raw workout data from SQL and uses it to calculate the number of new Peloton workouts.
        If there are new workouts, writes the new raw DataFrames to SQL, processes the raw DataFrames, and 
        writes the new processed DataFrame to SQL. '''
        
        self.py_conn = PylotonCycle(const.PELOTON_USERNAME, const.PELOTON_PASSWORD) 
        self.df_raw_workouts_data_in_sql = self.ingest_raw_workout_data_from_sql()

        total_workouts = self.py_conn.GetMe()["total_workouts"]
        existing_workouts = self.df_raw_workouts_data_in_sql.shape[0]
        self.new_workouts_num = total_workouts - existing_workouts

        print(f"Total Workouts: {total_workouts}")
        print(f"Workouts in Database: {existing_workouts}")
        print(f"New Workouts to Write: {self.new_workouts_num}\n")

        if self.new_workouts_num > 0:
            self.new_workouts = True

            # Double-check that `new_workout_num` is correct
            workouts_from_peloton = pd.DataFrame(self.py_conn.GetRecentWorkouts(self.new_workouts_num + 1))  # returns a list of dicts
            workouts_from_peloton['workout_id'] = [x for x in workouts_from_peloton['id'].tolist()]
            workout_ids_from_peloton = workouts_from_peloton['workout_id']
            last_non_new_workout_on_peloton = workout_ids_from_peloton.iloc[-1]
            print(f"Last non-new workout on Peloton: {workout_ids_from_peloton.iloc[-1]}")

            df_raw_workouts_data_sorted = self.df_raw_workouts_data_in_sql.sort_values(by=['start_time'])
            workout_ids_from_sql = df_raw_workouts_data_sorted['workout_id']
            last_workout_id_from_sql = workout_ids_from_sql.iloc[-1]
            print(f"Last workout on SQL: {workout_ids_from_sql.iloc[-1]}")

            workout_ids_check_bool = last_non_new_workout_on_peloton == last_workout_id_from_sql
            print(f"Are they the same?  {workout_ids_check_bool}\n")

            if not workout_ids_check_bool:
                print("There was a problem with data ingestion: workout IDs did not match.")
                print("Peloton Workout IDs:\n")
                print(workout_ids_from_peloton)
                print("SQL Workout IDs:\n")
                print(workout_ids_from_sql)
                exit()
     
            # Pull new workout data from Peloton
            print(f"Pulling data for {self.new_workouts_num} new workouts from Peloton...\n")
            self.df_raw_workout_data_new = workouts_from_peloton.drop(index=workouts_from_peloton.index[-1])
            self.df_raw_workout_metrics_data_new = self.pull_new_raw_metrics_data_from_peloton()

            # Write the new raw data to SQL
            self.export_new_raw_workout_data_to_sql()
            self.export_new_raw_metrics_data_to_sql()
            
            # Process the new raw data
            df_processed_new = self.process_workouts_from_new_raw_data()

            # Write the new processed data to SQL
            self.export_new_processed_data_to_sql(df_processed_new)

            # Update the `df_processed` attribute from SQL again
            self.df_processed = self.ingest_processed_data_from_sql()


    # DEPRECATED
    def __pull_new_raw_workouts_data_from_peloton(self) -> pd.DataFrame:  
        """ Pulls the raw workout data from Peloton for the corresponding number of workouts. """

        return pd.DataFrame(self.py_conn.GetRecentWorkouts(self.new_workouts))
        

    def pull_new_raw_metrics_data_from_peloton(self) -> pd.DataFrame:
        workout_ids_list = [x for x in self.df_raw_workout_data_new['workout_id'].tolist()]
        workout_metrics_list = [self.py_conn.GetWorkoutMetricsById(workout_id) for workout_id in workout_ids_list]
            
        workout_metrics_df = pd.DataFrame(workout_metrics_list)
        workout_metrics_df["id"] = [x for x in workout_ids_list]
        workout_metrics_df["workout_id"] = [x for x in workout_ids_list]

        return workout_metrics_df


    def export_new_raw_workout_data_to_sql(self):
        # Start by converting all datatypes (other than int64/float64) to strings for subsequent SQL export
        input_df = self.df_raw_workout_data_new
        for column in input_df.select_dtypes(exclude=['int64', 'float64', 'bool']).columns:
            input_df[column] = input_df[column].astype("string")

        with self.sql_engine.connect() as conn:
            input_df.to_sql("raw_data_workouts", conn, if_exists="append", index=False)


    def export_new_raw_metrics_data_to_sql(self):
        # Start by converting all datatypes (other than int64/float64) to strings for subsequent SQL export
        input_df = self.df_raw_workout_metrics_data_new
        for column in input_df.select_dtypes(exclude=['int64', 'float64', 'bool']).columns:
            input_df[column] = input_df[column].astype("string")
            
        with self.sql_engine.connect() as conn:
            input_df.to_sql("raw_data_metrics", conn, if_exists="append", index=False)


    def export_new_processed_data_to_sql(self, df_processed_new: pd.DataFrame):
        with self.sql_engine.connect() as conn:
            df_processed_new.to_sql("peloton", conn, if_exists="append", index=False)


    def ingest_raw_workout_data_from_sql(self) -> pd.DataFrame:
        with self.sql_engine.connect() as conn:
            df = pd.read_sql("SELECT * from raw_data_workouts", conn)
        return df


    def ingest_raw_metrics_data_from_sql(self) -> pd.DataFrame:
        with self.sql_engine.connect() as conn:
            df = pd.read_sql("SELECT * from raw_data_metrics", conn)
        return df


    def ingest_processed_data_from_sql(self) -> pd.DataFrame:
        with self.sql_engine.connect() as conn:
            df = pd.read_sql("SELECT * from peloton", conn)
        return df


    def print_processed_data_to_stdout(self) -> None:
        df = self.df_processed
        df['start_time_strf'] = [datetime.fromisoformat(x).strftime('%a %h %d %I:%M %p') 
                                                                for x in df['start_time_iso'].tolist()]
        print(df[['start_time_strf', 'ride_title', 'instructor_name', 'total_output', 
                                                'distance', 'calories', 'heart_rate_avg', 'strive_score']].tail(15))


    def process_workouts_from_new_raw_data(self) -> pd.DataFrame:
        df_workouts = self.df_raw_workout_data_new.set_index("id")
        df_workout_metrics = self.df_raw_workout_metrics_data_new.set_index("id")

        ride_group_list = []

        for row in df_workouts.itertuples():
            df_workout_ride = pd.json_normalize(ast.literal_eval(row.ride))
            workout_id = row.workout_id
            ride_attributes_dict = {}

            # Loop through the regular columns in df_workout and then the "ride" columns
            ride_attributes_dict.update({ label: data for label, data in row._asdict().items() })
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


def main():
    print("This is a module, not a script.")

if __name__ == '__main__':
    main()