import urllib3
import io
import json
from pathlib import Path
from datetime import datetime
from typing import Protocol
from enum import Enum

import pandas as pd

from peloton.helpers.constants import (DF_DTYPES_DICT, 
                                       PELOTON_PASSWORD,
                                       PELOTON_USERNAME, 
                                       WORKOUT_IMAGES_DIR, 
                                       ACHIEVEMENT_IMAGES_DIR,
                                       INSTRUCTORS_JSON,
                                       DATA_DIR,
                                       WORKOUTS_DIR,
                                       EASTERN_TIME)
from peloton.helpers.exceptions import WorkoutMismatchError
from peloton.helpers.functions import download_image, save_image, create_thumbnail
from peloton.handlers import (PelotonChartMaker, PylotonZMV,
                              PelotonPivots, PelotonMongoDB)
from peloton.models import (PelotonMetrics, PelotonSummary,
                            PelotonWorkoutData)


class PelotonDatabase(Protocol):
    def get_workout_id_list(self) -> list[str]: 
        """
        _summary_

        Returns:
            _description_
        """
        ...
    def ingest_workouts(self) -> list[PelotonWorkoutData]: ...
    def export_workout(self, workout: PelotonWorkoutData) -> None: ...
    def update_workout(self, workout: PelotonWorkoutData) -> None: ...
    def get_workout(self, workout_id: str) -> PelotonWorkoutData: ...
    def get_instructor(self, instructor_id: str) -> dict: ...
    def add_instructor(self, instructor: dict) -> None: ...   


class PelotonDBType(Enum):
    MONGODB = 'MongoDB'
    SQLITE = 'SQLite'
    MARIADB = 'MariaDB'
    POSTGRES = 'PostgreSQL'
    MYSQL = 'MySQL'


def get_peloton_db(db_type: PelotonDBType) -> PelotonDatabase:
    if db_type == PelotonDBType.MONGODB:
        return PelotonMongoDB()


class PelotonProcessor():   
    """Primary class for doing Peloton stuff!
    
    Attributes
    ----------
    py_conn : PylotonZMV
        Connection objeczt w/ methods for pulling data from Peloton
    db : PelotonDatabase
        Protocol class for internal database connector (defaults to PelotonMongoDB)
    workouts : list[PelotonWorkoutData]
        List of Pydantic models w/ workout data
    processed_df : pd.DataFrame
        Custom Pandas dataframe constructed from workout data
    pivots : PelotonPivots
        Object w/ methods for creating & printing pivot tables from workout data
    chart_maker : PelotonChartMaker
        Object w/ methods for creating chart tables & graphs from workout data

    """
    
    def __init__(self, 
                 username: str = PELOTON_USERNAME, 
                 password: str = PELOTON_PASSWORD,
                 db_type: PelotonDBType = PelotonDBType.MONGODB
                 ) -> None:
        self.py_conn = PylotonZMV(username, password)
        self.db = get_peloton_db(db_type)
        self.workouts = self.db.ingest_workouts()
        self.new_workouts = False
        self.processed_df = self.make_dataframe() if len(self.workouts) > 0 else None
        self.pivots = PelotonPivots(self.processed_df) if self.processed_df is not None else None
        self.chart_maker = PelotonChartMaker(self.workouts, self.pivots)
    
    def check_for_new_workouts(self) -> None:       
        new_workout_ids = self._get_new_workout_ids()
        if len(new_workout_ids) == 0:
            self.new_workouts = False
            self.workouts = list()
            return None   # everything below will only happen if there are new workouts!

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
            self.db.export_workout(workout)
            self.write_workout_to_json(workout)
            self.download_workout_image(workout)
            self.download_achievement_images(workout)

        self.new_workouts = True
        
        self.workouts = self.db.ingest_workouts()
        
        self.processed_df = self.make_dataframe()
        if self.pivots is not None:
            self.pivots.regenerate_tables(self.processed_df)
        self.chart_maker = PelotonChartMaker(self.workouts, self.pivots)
        self.write_csv_files()

    def get_workouts(self) -> list[PelotonWorkoutData]:
        return self.db.ingest_workouts()

    def _get_new_workout_ids(self) -> list[str]:
        workouts_on_peloton_num = self.py_conn.get_total_workouts_num()
        workouts_on_disk_num = len(self.db.get_workout_id_list())
        new_workouts_num = workouts_on_peloton_num - workouts_on_disk_num

        workout_ids_on_peloton = self.py_conn.get_workout_ids()
        workout_ids_on_disk = self.db.get_workout_id_list()
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

    def download_workout_image(self, workout: PelotonWorkoutData) -> None:
        if workout.summary.ride.image_url is None:
            print(f"No image available for workout {workout.workout_id}.")
            return None
        
        print(f"Downloading image for workout {workout.workout_id}...")
        image_data = download_image(workout.summary.ride.image_url)
        image_filename = workout.summary.ride.image_local_filename
        if image_data is not None:
            print(f"Downloaded!  Saving to disk and creating thumbnail...")
            save_image(image_data, image_filename, WORKOUT_IMAGES_DIR)
            create_thumbnail(image_data, image_filename, WORKOUT_IMAGES_DIR)

    def download_achievement_images(self, workout: PelotonWorkoutData) -> None:
        num_achievements = len(workout.summary.achievements)
        if num_achievements == 0:
            return None
        
        print(f"Downloading {num_achievements} achievement images for workout {workout.workout_id}...")
        for achievement in workout.summary.achievements:
            if achievement.image_url is not None:
                image_data = download_image(achievement.image_url)
                image_filename = achievement.image_local_filename
                if image_data is not None:
                    print(f"Downloaded!  Saving to disk...")
                    save_image(image_data, image_filename, ACHIEVEMENT_IMAGES_DIR)

    def make_list_of_dicts(self) -> list[dict]:
        return [workout.create_dictionary() for workout in self.workouts]

    def get_workout_object_from_id(self, workout_id: str) -> PelotonWorkoutData | None:
        ''' Get a `PelotonWorkoutData` object from its corresponding workout ID. '''
        workouts_by_id = {workout.summary.workout_id: workout for workout in self.workouts}
        return workouts_by_id.get(workout_id, None)

    def print_processed_data_to_stdout(self) -> None:
        df = self.processed_df.copy()
        if isinstance(df['start_time'].dtype, pd.DatetimeTZDtype):
            df['start_time_strf'] = [x.tz_convert(EASTERN_TIME).strftime('%a %h %d %I:%M %p') 
                                        for x in df['start_time'].tolist()]
        else:
            df['start_time_strf'] = [datetime.fromisoformat(x).strftime('%a %h %d %I:%M %p') 
                                        for x in df['start_time'].tolist()]
        print("")
        print(df[['start_time_strf', 'title', 'instructor_name', 'total_output', 
                    'distance', 'calories', 'avg_heart_rate', 'effort_score']].tail(15))

    def print_pivot_tables_to_stdout(self) -> None:
        print("")
        print("                             GRAND TOTALS")
        print(self.pivots.totals_table)
        print("")
        print(self.pivots.year_table)
        print("")
        print(self.pivots.month_table)

    def write_csv_files(self) -> None:
        self.processed_df.to_csv(DATA_DIR.joinpath('processed_workouts_data.csv'))

        self.pivots.regenerate_tables(self.processed_df)
        self.pivots.year_table.to_csv(DATA_DIR.joinpath('year_table.csv'))
        self.pivots.month_table.to_csv(DATA_DIR.joinpath('month_table.csv'))
        self.pivots.totals_table.to_csv(DATA_DIR.joinpath('totals_table.csv'))

    def get_workouts_from_json() -> list[PelotonWorkoutData]:
        try:
            json_files = [file for file in WORKOUTS_DIR.iterdir() if file.suffix == '.json']
        except FileNotFoundError as e:
            print(e)
            return list()
        
        if len(json_files) == 0:
            print(f"No JSON files found in {WORKOUTS_DIR}")
            return list()

        output_list = []
        for file in json_files:
            with open(file, 'r') as f:
                workout = PelotonWorkoutData.model_validate_json(f.read())
                output_list.append(workout)
                
        return output_list
    
    def write_workout_to_json(self, workout: PelotonWorkoutData) -> None:
        print(f"Writing JSON file for workout {workout.workout_id} to disk...")
        with open(WORKOUTS_DIR.joinpath(f"{workout.workout_id}.json"), 'w') as f:
            f.write(workout.model_dump_json(indent=4))

    def backup_all_workouts_to_json(self) -> None:
        for workout in self.workouts:
            print(f"Writing workout {workout.workout_id} to JSON...")
            self.write_workout_to_json(workout)

    def get_instructors_dict_from_json(self) -> dict:
        try:
            with open(INSTRUCTORS_JSON, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return dict()

    def add_instructor_to_json(self, instructor: dict) -> None:
        """
        Takes a dictionary with Peloton instructor data and adds it to the
        master JSON file with all instructor data.

        Args:
            instructor (dict): asfdasdf
        """
        instructors_dict = self.get_instructors_dict_from_json()
        instructors_dict.update({instructor['instructor_id']: instructor})
        with open(INSTRUCTORS_JSON, 'w') as f:
            json.dump(instructors_dict, f, indent=4)

    def _reprocess_workout_data(self,
                              workout_list: list[PelotonWorkoutData] = None
                              ) -> list[PelotonWorkoutData]:        
        workout_list = self.workouts if workout_list is None else workout_list
        
        output_list = []
        for workout in workout_list:
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
            output_list.append(workout_data)

        return output_list

    def reprocess_json_data(self) -> None:
        ''' Re-ingests all workout data from the JSON files, reprocesses
        the data, and writes new JSON files. '''
        
        json_workout_list = self.get_workouts_from_json()
        new_workout_list = self._reprocess_workout_data(json_workout_list)

        for workout in new_workout_list:
            self.write_workout_to_json(workout)

    def reprocess_db_data(self) -> None:
        ''' Reprocesses the raw workout data in the database, 
        replaces the data in the database, and writes new JSON files. '''
        
        new_workout_list = self._reprocess_workout_data()
        self.workouts = new_workout_list
        self.processed_df = self.make_dataframe()

        for workout in self.workouts:
            self.db.update_workout(workout)
            self.write_workout_to_json(workout)

def main():
    print("This is a module, not a script.")

if __name__ == '__main__':
    main()