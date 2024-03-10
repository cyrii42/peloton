import pandas as pd
import sqlalchemy as db

from peloton.constants import (PELOTON_CSV_DIR, PELOTON_PASSWORD,
                               PELOTON_USERNAME, DF_DTYPES_DICT, WORKOUTS_DIR)
from peloton.pyloton_zmv import PylotonZMV
from peloton.handlers import PelotonSQL, PelotonStdoutPrinter, PelotonJSONWriter, PelotonCSVWriter, PelotonChartMaker, PelotonMongoDB
from peloton.schema import PelotonPivots, PelotonWorkoutData, PelotonSummary, PelotonMetrics
from peloton.exceptions import WorkoutMismatchError


class PelotonProcessor():
    ''' 
    Object for pulling new data from Peloton, processing it, and exporting to SQL. 

    Parameters:
    - `sql_engine` (`db.Engine`, optional): The SQL engine to use for exporting data. Defaults to `None`.
    - `username` (`str`): The Peloton username. Defaults to `PELOTON_USERNAME`.
    - `password` (`str`): The Peloton password. Defaults to `PELOTON_PASSWORD`.
    '''

    def __init__(self, sql_engine: db.Engine = None, username: str = PELOTON_USERNAME, password: str = PELOTON_PASSWORD):
        self.py_conn = PylotonZMV(username, password)
        self.mongodb = PelotonMongoDB()
        self.workouts = self.mongodb.ingest_workouts_from_mongodb()
        self.new_workouts = False
        if sql_engine is not None:
            self.sql_writer = PelotonSQL(sql_engine)
        self.processed_df = self.make_dataframe() if len(self.workouts) > 0 else None
        self.pivots = PelotonPivots(self.processed_df) if self.processed_df is not None else None
        self.chart_maker = PelotonChartMaker(self.workouts)


    def check_for_new_workouts(self) -> None:
        ''' Check for new workouts on Peloton and update the internal state accordingly. '''
        
        new_workout_ids = self._get_new_workout_ids()
        if len(new_workout_ids) == 0:
            self.new_workouts = False
            return list()

        print(f"New Workout IDs:  {new_workout_ids}")
        new_workout_list: list[PelotonWorkoutData] = []
        for workout_id in new_workout_ids:
            summary_raw = self.py_conn.get_workout_summary_by_id(workout_id)
            metrics_raw = self.py_conn.get_workout_metrics_by_id(workout_id)
            workout_data = PelotonWorkoutData(
                workout_id=workout_id,
                summary_raw=summary_raw,
                metrics_raw=metrics_raw,
                summary=PelotonSummary(**summary_raw),
                metrics=PelotonMetrics(**metrics_raw)
                )
            new_workout_list.append(workout_data)

        for workout in new_workout_list:
            # self.json_writer.write_workout_to_json(workout)
            self.mongodb.export_workout_to_mongodb(workout)
            self.mongodb.write_workout_to_json(workout)

        self.new_workouts = True
        
        # self.json_writer.refresh_data()
        # self.workouts = self.get_workouts_from_json()
        self.workouts = self.mongodb.ingest_workouts_from_mongodb()
        
        self.processed_df = self.make_dataframe()
        if self.pivots is not None:
            self.pivots.regenerate_tables(self.processed_df)

    def get_workouts_from_mongodb(self) -> list[PelotonWorkoutData]:
        ''' Get the list of workouts from the MongoDB database. '''
        
        return self.mongodb.ingest_workouts_from_mongodb()

    def get_workouts_from_sql(self) -> list[PelotonWorkoutData]:
        ''' Get the list of workouts from the SQL database. '''
        
        return self.sql_writer.ingest_workouts_from_sql()

    def get_workouts_from_json(self) -> list[PelotonWorkoutData]:
        ''' Get the list of workouts from the JSON files. '''
        
        self.json_writer.refresh_data()

        return self.json_writer.get_workouts_from_json()

    def reprocess_json_data(self) -> None:
        ''' Reprocess the JSON data and update the internal state accordingly. '''
        
        self.json_writer.refresh_data()
        self.workouts = self.get_workouts_from_json()

        workout_list = []
        for workout in self.workouts:
            workout_id = workout.workout_id
            summary_raw = workout.summary_raw
            metrics_raw = workout.metrics_raw
            workout_data = PelotonWorkoutData(
                workout_id=workout_id,
                summary_raw=summary_raw,
                metrics_raw=metrics_raw,
                summary=PelotonSummary(**summary_raw),
                metrics=PelotonMetrics(**metrics_raw)
                )
            workout_list.append(workout_data)

        self.workouts = workout_list
        self.processed_df = self.make_dataframe()

        for workout in self.workouts:
            self.json_writer.write_workout_to_json(workout)

    def _get_new_workout_ids(self) -> list[str]:
        ''' Get the IDs of new workouts on Peloton. '''
        
        # self.json_writer.refresh_data()

        workouts_on_peloton_num = self.py_conn.get_total_workouts_num()
        # workouts_on_disk_num = self.json_writer.total_workouts_on_disk
        workouts_on_disk_num = len(self.mongodb.get_workout_id_list_from_mongodb())
        new_workouts_num = workouts_on_peloton_num - workouts_on_disk_num

        workout_ids_on_peloton = self.py_conn.get_workout_ids()
        # workout_ids_on_disk = self.json_writer.get_workout_ids_from_json()
        workout_ids_on_disk = self.mongodb.get_workout_id_list_from_mongodb()
        new_workout_ids = [workout_id for workout_id in workout_ids_on_peloton
                            if workout_id not in workout_ids_on_disk]

        if len(new_workout_ids) != new_workouts_num:
            raise WorkoutMismatchError()

        print(f"Total Workouts: {len(workout_ids_on_peloton)}")
        print(f"Workouts in Database: {len(workout_ids_on_disk)}")
        print(f"New Workouts to Write: {len(new_workout_ids)}")

        return new_workout_ids

    def _convert_workout_list_to_dataframe(self, workout_list: list[PelotonWorkoutData]) -> pd.DataFrame:
        if len(workout_list) > 0:
            output_df = (pd.concat([workout.create_dataframe() for workout in workout_list], ignore_index=True)
                           .sort_values(by=['start_time'])
                           .reset_index(drop=True))
            output_df = output_df.astype({key: value for key, value in DF_DTYPES_DICT.items() if key in output_df.columns}, errors='ignore')              
            return output_df
                                #  if (key in output_df.columns) and (output_df[key].notna())})
        else:
            return pd.DataFrame()

    def make_dataframe(self) -> pd.DataFrame:
        print("Creating processed Dataframe...")
        workout_df_list = [workout.create_dataframe() for workout in self.workouts]
        output_df = (pd.concat(workout_df_list, ignore_index=True)
                       .sort_values(by='start_time')
                       .reset_index(drop=True))
        output_df = output_df.astype({key: value for key, value in DF_DTYPES_DICT.items() if key in output_df.columns}, errors='ignore')               
        return output_df
                                #  if (key in output_df.columns) and (output_df[key].notna())})

    def get_workout_object_from_id(self, workout_id: str) -> PelotonWorkoutData:
        ''' Get the workout object from the workout ID. '''
        return next((workout for workout in self.workouts if workout.workout_id == workout_id), None)
    
    # def get_full_dataframe(self) -> pd.DataFrame:
    #     self.json_writer.refresh_data()

    #     df_existing = self._convert_workout_list_to_dataframe(self.json_writer.get_workout_data_from_json())
    #     df_new = self._convert_workout_list_to_dataframe(self.check_for_new_workouts())

    #     return (pd.concat([df_existing, df_new], ignore_index=True)
    #               .sort_values(by=['start_time'])
    #               .reset_index(drop=True))

    def create_new_pivot_tables(self, df_processed: pd.DataFrame) -> None:
        self.pivots.regenerate_tables(df_processed)

    def print_processed_data_to_stdout(self) -> None:
        peloton_printer = PelotonStdoutPrinter(self.processed_df)
        peloton_printer.print_processed_data()

    def print_pivot_tables_to_stdout(self) -> None:
        peloton_printer = PelotonStdoutPrinter(self.processed_df)
        peloton_printer.print_pivot_tables()

    def write_csv_files(self) -> None:
        ...

# class PelotonProcessorOld():   
#     ''' Object for pulling new data from Peloton, processing it, and exporting to SQL. '''
    
#     def __init__(self, sql_engine: db.Engine):
#         self.sql_writer = PelotonSQL(sql_engine)
#         self.new_workouts = False
#         self.new_workouts_num = 0
#         self.df_raw_workout_data = self.ingest_raw_workout_data_from_sql()
#         self.df_raw_metrics_data = self.ingest_raw_metrics_data_from_sql()
#         self.df_processed = self.ingest_processed_data_from_sql()
#         self.pivots = PelotonPivots(self.df_processed)


#     def check_for_new_workouts(self) -> None:
#         ''' Pulls raw workout data from SQL and uses it to calculate the number of new Peloton workouts.
#         If there are new workouts, writes the new raw DataFrames to SQL, processes the raw DataFrames, and 
#         writes the new processed DataFrame to SQL. '''
        
#         self.py_conn = PylotonCycle(PELOTON_USERNAME, PELOTON_PASSWORD) 
#         self.df_raw_workouts_data_in_sql = self.ingest_raw_workout_data_from_sql()

#         total_workouts = self.py_conn.GetMe()["total_workouts"]
#         existing_workouts = self.df_raw_workouts_data_in_sql.shape[0]
#         self.new_workouts_num = total_workouts - existing_workouts

#         print(f"Total Workouts: {total_workouts}")
#         print(f"Workouts in Database: {existing_workouts}")
#         print(f"New Workouts to Write: {self.new_workouts_num}")

#         # Double-check that `new_workout_num` is correct
#         workouts_from_peloton = pd.DataFrame(self.py_conn.GetRecentWorkouts(self.new_workouts_num + 1))  # returns a list of dicts
#         workouts_from_peloton['workout_id'] = [x for x in workouts_from_peloton['id'].tolist()]
#         workout_ids_from_peloton = workouts_from_peloton['workout_id']
#         last_non_new_workout_on_peloton = workout_ids_from_peloton.iloc[-1]
#         print(f"Last non-new workout on Peloton: {workout_ids_from_peloton.iloc[-1]}")

#         df_raw_workouts_data_sorted = self.df_raw_workouts_data_in_sql.sort_values(by=['start_time'])
#         workout_ids_from_sql = df_raw_workouts_data_sorted['workout_id']
#         last_workout_id_from_sql = workout_ids_from_sql.iloc[-1]
#         print(f"Last workout on SQL: {workout_ids_from_sql.iloc[-1]}")

#         workout_ids_check_bool = last_non_new_workout_on_peloton == last_workout_id_from_sql
#         print(f"Are they the same?  {workout_ids_check_bool}")

#         if not workout_ids_check_bool:
#             print("There was a problem with data ingestion: workout IDs did not match.")
#             print("Peloton Workout IDs:\n")
#             print(workout_ids_from_peloton)
#             print("SQL Workout IDs:\n")
#             print(workout_ids_from_sql)
#             exit()

#         if self.new_workouts_num > 0:
#             self.new_workouts = True

#             # Pull new workout data from Peloton
#             print(f"\nPulling data for {self.new_workouts_num} new workout(s) from Peloton...")
#             df_raw_workout_data_new = workouts_from_peloton.drop(index=workouts_from_peloton.index[-1])
#             df_raw_metrics_data_new = self.pull_new_raw_metrics_data_from_peloton(df_raw_workout_data_new)

#             # Process the new raw data
#             df_processed_new = self.process_new_workouts(df_raw_workout_data_new, df_raw_metrics_data_new)

#             # Write the new data to SQL
#             self.export_new_raw_workout_data_to_sql(df_raw_workout_data_new)
#             self.export_new_raw_metrics_data_to_sql(df_raw_metrics_data_new)
#             self.export_new_processed_data_to_sql(df_processed_new)

#             # Refresh all Dataframe attributes from SQL
#             self.df_raw_workout_data = self.ingest_raw_workout_data_from_sql()
#             self.df_raw_metrics_data = self.ingest_raw_metrics_data_from_sql()
#             self.df_processed = self.ingest_processed_data_from_sql()

#             # Create new pivot tables
#             self.pivots = PelotonPivots(self.df_processed)      

#     def pull_new_raw_metrics_data_from_peloton(self, df_workouts: pd.DataFrame) -> pd.DataFrame:
#         workout_ids_list = [x for x in df_workouts['workout_id'].tolist()]
#         workout_metrics_list = [self.py_conn.GetWorkoutMetricsById(workout_id) for workout_id in workout_ids_list]
            
#         workout_metrics_df = pd.DataFrame(workout_metrics_list)
#         workout_metrics_df["id"] = [x for x in workout_ids_list]
#         workout_metrics_df["workout_id"] = [x for x in workout_ids_list]

#         return workout_metrics_df

#     def process_new_workouts(self, df_workouts: pd.DataFrame, df_metrics: pd.DataFrame) -> pd.DataFrame:
#         '''
#         - From "Summary":
#             - Collects data in all of the "summary" columns
#             - Collects data in all of the "ride" columns
#         - From "Metrics":
#             - Collects total Output, Distance, and Calories from "Summaries"
#             - Collects avg & max values for Output, Cadence, Resistance, and Speed (creating "X_avg", "X_max" headers)
#             - Collects strive score and HR-zone durations from "effort_zones", if present
#         '''
#         df_workout_data = df_workouts.copy().set_index("id")
#         df_metrics_data = df_metrics.copy().set_index("id")

#         ride_group_list = []

#         for row in df_workout_data.itertuples():
#             df_workout_ride = pd.json_normalize(ast.literal_eval(row.ride))
#             workout_id = row.workout_id
#             ride_attributes_dict = {}

#             # Loop through the regular columns in df_workout and then the "ride" columns
#             ride_attributes_dict.update({ label: data for label, data in row._asdict().items() })
#             ride_attributes_dict.update({ f"ride_{column}": df_workout_ride[column][0] for column in df_workout_ride.columns })

#             # Pull the corresponding row of the Metrics DataFrame and put it into a Series
#             workout_metrics_series = df_metrics_data.loc[workout_id] 

#             # Loop through summaries (total_output, distance, calories)
#             df_summaries = pd.json_normalize(ast.literal_eval(workout_metrics_series["summaries"]))
#             ride_attributes_dict.update({ df_summaries["slug"][index]: df_summaries["value"][index] for index, row in df_summaries.iterrows() })

#             # Loop through average & max values (output, cadence, resistance, speed, HR)
#             df_metrics = pd.json_normalize(ast.literal_eval(workout_metrics_series["metrics"]))
#             df_average_values = df_metrics.set_index("slug")["average_value"]
#             df_max_values = df_metrics.set_index("slug")["max_value"]
#             ride_attributes_dict.update({ f"{index}_avg": value for index, value in df_average_values.items() })
#             ride_attributes_dict.update({ f"{index}_max": value for index, value in df_max_values.items() })

#             # Set "Strive Score" attribute & loop through HR Zone Duration columns
#             if workout_metrics_series.notna()["effort_zones"]:
#                 df_effort_zones = pd.json_normalize(ast.literal_eval(workout_metrics_series["effort_zones"]))

#                 ride_attributes_dict.update({ "strive_score": df_effort_zones["total_effort_points"][0] })
#                 for x in range(4):
#                     zone_num = x + 1
#                     column_name = f"heart_rate_zone_durations.heart_rate_z{zone_num}_duration"
#                     ride_attributes_dict.update({ column_name: df_effort_zones[column_name][0] })

#             # Create a PelotonRide object from the "ride_attributes_dict" dictionary
#             ride_object = PelotonRide.from_dict(ride_attributes_dict)

#             # Add new PelotonRide to the running list of PelotonRides (which will later be used to make a PelotonRideGroup object)
#             ride_group_list.append(ride_object)
#             print(f"Pulled and processed {ride_object.start_time_iso}")

#         # After the loop, create a PelotonRideGroup object from the list of PelotonRide objects
#         ride_group = PelotonRideGroup(ride_group_list)

#         # Return a DataFrame of the Peloton rides using the create_dataframe() method in the PelotonRideGroup object
#         output_df = ride_group.create_dataframe()
#         return output_df

#     def export_new_raw_workout_data_to_sql(self, input_df: pd.DataFrame):
#         self.sql_writer.export_data_to_sql(input_df, 'raw_data_workouts')

#     def export_new_raw_metrics_data_to_sql(self, input_df: pd.DataFrame):
#         self.sql_writer.export_data_to_sql(input_df, 'raw_data_metrics')

#     def export_new_processed_data_to_sql(self, df_processed_new: pd.DataFrame):
#         self.sql_writer.export_data_to_sql(df_processed_new, 'peloton')

#     def ingest_raw_workout_data_from_sql(self) -> pd.DataFrame:
#         output_df = self.sql_writer.ingest_data_from_sql(table_name='raw_data_workouts')
#         return output_df

#     def ingest_raw_metrics_data_from_sql(self) -> pd.DataFrame:
#         output_df = self.sql_writer.ingest_data_from_sql(table_name='raw_data_metrics')
#         return output_df

#     def ingest_processed_data_from_sql(self) -> pd.DataFrame:
#         output_df = self.sql_writer.ingest_data_from_sql(table_name='peloton')
#         return output_df

#     def create_new_pivot_tables(self, df_processed: pd.DataFrame) -> None:
#         self.pivots.regenerate_tables(df_processed)

#     def print_processed_data_to_stdout(self) -> None:
#         peloton_printer = PelotonStdoutPrinter(self.ingest_processed_data_from_sql())
#         peloton_printer.print_processed_data()

#     def print_pivot_tables_to_stdout(self) -> None:
#         peloton_printer = PelotonStdoutPrinter(self.ingest_processed_data_from_sql())
#         peloton_printer.print_pivot_tables()

#     def write_csv_files(self) -> None:
#         df_processed = self.ingest_processed_data_from_sql()
#         df_raw_workouts_data = self.ingest_raw_workout_data_from_sql()
#         df_raw_metrics_data = self.ingest_raw_metrics_data_from_sql()
        
#         df_processed.to_csv(f"{PELOTON_CSV_DIR}/processed_workouts_data.csv")
#         df_raw_workouts_data.to_csv(f"{PELOTON_CSV_DIR}/raw_workouts_data.csv")
#         df_raw_metrics_data.to_csv(f"{PELOTON_CSV_DIR}/raw_metrics_data.csv")
        
#         self.pivots.year_table.to_csv(f"{PELOTON_CSV_DIR}/year_table.csv")
#         self.pivots.month_table.to_csv(f"{PELOTON_CSV_DIR}/month_table.csv")
#         self.pivots.totals_table.to_csv(f"{PELOTON_CSV_DIR}/totals_table.csv")
        

#     # DEPRECATED
#     def _pull_new_raw_workouts_data_from_peloton(self) -> pd.DataFrame:  
#         """ Pulls the raw workout data from Peloton for the corresponding number of workouts. """

#         return pd.DataFrame(self.py_conn.GetRecentWorkouts(self.new_workouts))


def main():
    print("This is a module, not a script.")

if __name__ == '__main__':
    main()