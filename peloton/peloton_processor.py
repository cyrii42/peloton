import pandas as pd
import sqlalchemy as db

from peloton.constants import (DF_DTYPES_DICT, PELOTON_PASSWORD,
                               PELOTON_USERNAME)
from peloton.exceptions import WorkoutMismatchError
from peloton.handlers import (PelotonChartMaker, PelotonCSVWriter,
                              PelotonImageDownloader, PelotonMongoDB, 
                              PelotonSQL, PelotonStdoutPrinter)
from peloton.pyloton_zmv import PylotonZMV
from peloton.schema import (PelotonMetrics, PelotonPivots, PelotonSummary,
                            PelotonWorkoutData)


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
        self.chart_maker = PelotonChartMaker(self.workouts, self.pivots)
        self.image_downloader = PelotonImageDownloader()

    def check_for_new_workouts(self) -> None:
        ''' Check for new workouts on Peloton and update the internal state accordingly. '''
        
        new_workout_ids = self._get_new_workout_ids()
        if len(new_workout_ids) == 0:
            self.new_workouts = False
            return list()   # everything below will only happen if there are new workouts!

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
            self.image_downloader.download_workout_image(workout)

        self.new_workouts = True
        
        # self.json_writer.refresh_data()
        # self.workouts = self.get_workouts_from_json()
        self.workouts = self.mongodb.ingest_workouts_from_mongodb()
        
        self.processed_df = self.make_dataframe()
        if self.pivots is not None:
            self.pivots.regenerate_tables(self.processed_df)
        self.chart_maker = PelotonChartMaker(self.workouts, self.pivots)
        self.write_csv_files()

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

    def reprocess_mongodb_data(self) -> None:
        ''' Reprocesses the raw workout data in MongoDB, replaces the data in MongoDB, and writes new JSON files. '''
        
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
            self.mongodb.update_workout_in_mongodb(workout)
            self.mongodb.write_workout_to_json(workout)
    
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

        workouts_on_peloton_num = self.py_conn.get_total_workouts_num()
        workouts_on_disk_num = len(self.mongodb.get_workout_id_list_from_mongodb())
        new_workouts_num = workouts_on_peloton_num - workouts_on_disk_num

        workout_ids_on_peloton = self.py_conn.get_workout_ids()
        workout_ids_on_disk = self.mongodb.get_workout_id_list_from_mongodb()
        new_workout_ids = [workout_id for workout_id in workout_ids_on_peloton
                            if workout_id not in workout_ids_on_disk]

        if len(new_workout_ids) != new_workouts_num:
            raise WorkoutMismatchError()

        print(f"Total Workouts: {len(workout_ids_on_peloton)}")
        print(f"Workouts in Database: {len(workout_ids_on_disk)}")
        print(f"New Workouts to Write: {len(new_workout_ids)}")

        return new_workout_ids

    def make_dataframe(self) -> pd.DataFrame:
        print("Creating processed Dataframe...")
        workout_dict_list = [workout.create_dictionary() for workout in self.workouts]
        output_df = (pd.DataFrame(workout_dict_list)
                     .dropna(axis='columns', how='all')
                     .drop(columns=['duration'])
                     .sort_values(by='start_time')
                     .reset_index(drop=True))
        output_df = output_df.astype({key: value for key, value in DF_DTYPES_DICT.items() if key in output_df.columns}, errors='ignore')               
        return output_df

    def get_workout_object_from_id(self, workout_id: str) -> PelotonWorkoutData:
        ''' Get a `PelotonWorkoutData` object from its corresponding workout ID. '''
        return next((workout for workout in self.workouts if workout.workout_id == workout_id), None)

    def create_new_pivot_tables(self, df_processed: pd.DataFrame) -> None:
        self.pivots.regenerate_tables(df_processed)

    def print_processed_data_to_stdout(self) -> None:
        peloton_printer = PelotonStdoutPrinter(self.processed_df)
        peloton_printer.print_processed_data()

    def print_pivot_tables_to_stdout(self) -> None:
        peloton_printer = PelotonStdoutPrinter(self.processed_df)
        peloton_printer.print_pivot_tables()

    def write_csv_files(self) -> None:
        csv_writer = PelotonCSVWriter(self.processed_df)
        csv_writer.write_csv_files()

def main():
    print("This is a module, not a script.")

if __name__ == '__main__':
    main()