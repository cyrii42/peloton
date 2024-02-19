import ast

import pandas as pd
import sqlalchemy as db
from pylotoncycle import PylotonCycle

from peloton.constants import (PELOTON_CSV_DIR, PELOTON_PASSWORD,
                               PELOTON_USERNAME)
from peloton.peloton_pivots import PelotonPivots
from peloton.peloton_printer import PelotonPrinter
from peloton.peloton_ride import PelotonRide, PelotonRideGroup
from peloton.peloton_sql import PelotonSQL

'''
METHODS:
check_for_new_workouts
pull_new_raw_metrics_data_from_peloton
export_new_raw_workout_data_to_sql
export_new_raw_metrics_data_to_sql
export_new_processed_data_to_sql
ingest_raw_workout_data_from_sql
ingest_raw_metrics_data_from_sql
ingest_processed_data_from_sql
print_processed_data_to_stdout
process_workouts_from_new_raw_data

INSTANCE VARIABLES:
sql_engine (from __init__())
new_workouts: bool (from __init__())
new_workouts_num: int (from __init__())
df_processed:  pd.DataFrame (from __init__())

py_conn (created in check_for_new_workouts)
df_raw_workouts_data_in_sql (created in check_for_new_workouts)
df_raw_workout_data_new (created in check_for_new_workouts)
df_raw_workout_metrics_data_new (created in check_for_new_workouts)
'''

class PelotonProcessor():   
    ''' Object for pulling new data from Peloton, processing it, and exporting to SQL. '''
    
    def __init__(self, sql_engine: db.Engine):
        self.sql_writer = PelotonSQL(sql_engine)
        self.new_workouts = False
        self.new_workouts_num = 0
        self.df_raw_workout_data = self.ingest_raw_workout_data_from_sql()
        self.df_raw_metrics_data = self.ingest_raw_metrics_data_from_sql()
        self.df_processed = self.ingest_processed_data_from_sql()
        self.pivots = PelotonPivots(self.df_processed)


    def check_for_new_workouts(self) -> None:
        ''' Pulls raw workout data from SQL and uses it to calculate the number of new Peloton workouts.
        If there are new workouts, writes the new raw DataFrames to SQL, processes the raw DataFrames, and 
        writes the new processed DataFrame to SQL. '''
        
        self.py_conn = PylotonCycle(PELOTON_USERNAME, PELOTON_PASSWORD) 
        self.df_raw_workouts_data_in_sql = self.ingest_raw_workout_data_from_sql()

        total_workouts = self.py_conn.GetMe()["total_workouts"]
        existing_workouts = self.df_raw_workouts_data_in_sql.shape[0]
        self.new_workouts_num = total_workouts - existing_workouts

        print(f"Total Workouts: {total_workouts}")
        print(f"Workouts in Database: {existing_workouts}")
        print(f"New Workouts to Write: {self.new_workouts_num}")

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
        print(f"Are they the same?  {workout_ids_check_bool}")

        if not workout_ids_check_bool:
            print("There was a problem with data ingestion: workout IDs did not match.")
            print("Peloton Workout IDs:\n")
            print(workout_ids_from_peloton)
            print("SQL Workout IDs:\n")
            print(workout_ids_from_sql)
            exit()

        if self.new_workouts_num > 0:
            self.new_workouts = True

            # Pull new workout data from Peloton
            print(f"\nPulling data for {self.new_workouts_num} new workout(s) from Peloton...")
            df_raw_workout_data_new = workouts_from_peloton.drop(index=workouts_from_peloton.index[-1])
            df_raw_metrics_data_new = self.pull_new_raw_metrics_data_from_peloton(df_raw_workout_data_new)

            # Process the new raw data
            df_processed_new = self.process_new_workouts(df_raw_workout_data_new, df_raw_metrics_data_new)

            # Write the new data to SQL
            self.export_new_raw_workout_data_to_sql(df_raw_workout_data_new)
            self.export_new_raw_metrics_data_to_sql(df_raw_metrics_data_new)
            self.export_new_processed_data_to_sql(df_processed_new)

            # Refresh all Dataframe attributes from SQL
            self.df_raw_workout_data = self.ingest_raw_workout_data_from_sql()
            self.df_raw_metrics_data = self.ingest_raw_metrics_data_from_sql()
            self.df_processed = self.ingest_processed_data_from_sql()

            # Create new pivot tables
            self.pivots = PelotonPivots(self.df_processed)      

    def pull_new_raw_metrics_data_from_peloton(self, df_workouts: pd.DataFrame) -> pd.DataFrame:
        workout_ids_list = [x for x in df_workouts['workout_id'].tolist()]
        workout_metrics_list = [self.py_conn.GetWorkoutMetricsById(workout_id) for workout_id in workout_ids_list]
            
        workout_metrics_df = pd.DataFrame(workout_metrics_list)
        workout_metrics_df["id"] = [x for x in workout_ids_list]
        workout_metrics_df["workout_id"] = [x for x in workout_ids_list]

        return workout_metrics_df

    def process_new_workouts(self, df_workouts: pd.DataFrame, df_metrics: pd.DataFrame) -> pd.DataFrame:
        '''
        - From "Summary":
            - Collects data in all of the "summary" columns
            - Collects data in all of the "ride" columns
        - From "Metrics":
            - Collects total Output, Distance, and Calories from "Summaries"
            - Collects avg & max values for Output, Cadence, Resistance, and Speed (creating "X_avg", "X_max" headers)
            - Collects strive score and HR-zone durations from "effort_zones", if present
        '''
        df_workout_data = df_workouts.copy().set_index("id")
        df_metrics_data = df_metrics.copy().set_index("id")

        ride_group_list = []

        for row in df_workout_data.itertuples():
            df_workout_ride = pd.json_normalize(ast.literal_eval(row.ride))
            workout_id = row.workout_id
            ride_attributes_dict = {}

            # Loop through the regular columns in df_workout and then the "ride" columns
            ride_attributes_dict.update({ label: data for label, data in row._asdict().items() })
            ride_attributes_dict.update({ f"ride_{column}": df_workout_ride[column][0] for column in df_workout_ride.columns })

            # Pull the corresponding row of the Metrics DataFrame and put it into a Series
            workout_metrics_series = df_metrics_data.loc[workout_id] 

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

            # Create a PelotonRide object from the "ride_attributes_dict" dictionary
            ride_object = PelotonRide.from_dict(ride_attributes_dict)

            # Add new PelotonRide to the running list of PelotonRides (which will later be used to make a PelotonRideGroup object)
            ride_group_list.append(ride_object)
            print(f"Pulled and processed {ride_object.start_time_iso}")

        # After the loop, create a PelotonRideGroup object from the list of PelotonRide objects
        ride_group = PelotonRideGroup(ride_group_list)

        # Return a DataFrame of the Peloton rides using the create_dataframe() method in the PelotonRideGroup object
        output_df = ride_group.create_dataframe()
        return output_df

    def export_new_raw_workout_data_to_sql(self, input_df: pd.DataFrame):
        self.sql_writer.export_data_to_sql(input_df, 'raw_data_workouts')

    def export_new_raw_metrics_data_to_sql(self, input_df: pd.DataFrame):
        self.sql_writer.export_data_to_sql(input_df, 'raw_data_metrics')

    def export_new_processed_data_to_sql(self, df_processed_new: pd.DataFrame):
        self.sql_writer.export_data_to_sql(df_processed_new, 'peloton')

    def ingest_raw_workout_data_from_sql(self) -> pd.DataFrame:
        output_df = self.sql_writer.ingest_data_from_sql(table_name='raw_data_workouts')
        return output_df

    def ingest_raw_metrics_data_from_sql(self) -> pd.DataFrame:
        output_df = self.sql_writer.ingest_data_from_sql(table_name='raw_data_metrics')
        return output_df

    def ingest_processed_data_from_sql(self) -> pd.DataFrame:
        output_df = self.sql_writer.ingest_data_from_sql(table_name='peloton')
        return output_df

    def create_new_pivot_tables(self, df_processed: pd.DataFrame) -> None:
        self.pivots.regenerate_tables(df_processed)

    def print_processed_data_to_stdout(self) -> None:
        peloton_printer = PelotonPrinter(self.ingest_processed_data_from_sql())
        peloton_printer.print_processed_data()

    def print_pivot_tables_to_stdout(self) -> None:
        peloton_printer = PelotonPrinter(self.ingest_processed_data_from_sql())
        peloton_printer.print_pivot_tables()

    def write_csv_files(self) -> None:
        df_processed = self.ingest_processed_data_from_sql()
        df_raw_workouts_data = self.ingest_raw_workout_data_from_sql()
        df_raw_metrics_data = self.ingest_raw_metrics_data_from_sql()
        
        df_processed.to_csv(f"{PELOTON_CSV_DIR}/processed_workouts_data.csv")
        df_raw_workouts_data.to_csv(f"{PELOTON_CSV_DIR}/raw_workouts_data.csv")
        df_raw_metrics_data.to_csv(f"{PELOTON_CSV_DIR}/raw_metrics_data.csv")
        
        self.pivots.year_table.to_csv(f"{PELOTON_CSV_DIR}/year_table.csv")
        self.pivots.month_table.to_csv(f"{PELOTON_CSV_DIR}/month_table.csv")
        self.pivots.totals_table.to_csv(f"{PELOTON_CSV_DIR}/totals_table.csv")
        

    # DEPRECATED
    def _pull_new_raw_workouts_data_from_peloton(self) -> pd.DataFrame:  
        """ Pulls the raw workout data from Peloton for the corresponding number of workouts. """

        return pd.DataFrame(self.py_conn.GetRecentWorkouts(self.new_workouts))


def main():
    print("This is a module, not a script.")

if __name__ == '__main__':
    main()