import ast
import json
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from pprint import pprint

import pandas as pd
import sqlalchemy as db
from pylotoncycle import PylotonCycle

from constants import PELOTON_PASSWORD, PELOTON_USERNAME

EASTERN_TIME = ZoneInfo('America/New_York')
TXT_DIR = Path('../data/raw_txt').resolve()
CSV_DIR = Path('../data/raw_csv').resolve()

        # self.total_workouts = self.py_conn.GetMe()["total_workouts"]
        # self.raw_workout_data = self.py_conn.GetRecentWorkouts(self.total_workouts)  # returns a list of dicts
        # self.workout_ids_list = [x for x in self.raw_workout_data['workout_id'].tolist()]
        # self.workout_metrics_list = [self.py_conn.GetWorkoutMetricsById(workout_id) for workout_id in self.workout_ids_list]


class PelotonTxtFiles():
    def __init__(self):
        self.py_conn = PylotonCycle(PELOTON_USERNAME, PELOTON_PASSWORD) 
        

    def get_data_from_peloton(self) -> None:
        # now_str = datetime.now(tz=EASTERN_TIME).strftime('%Y-%m-%d_%H-%M')
        
        self.workout_list = self.get_workout_list()
        # self.dump_workout_list_to_txt(now_str)
        
        self.workout_ids = self.get_workout_ids()
        # self.dump_workout_ids_to_txt(now_str)
        
        self.workouts_by_id = self.get_workouts_by_id()
        # self.dump_workouts_by_id_to_txt(now_str)
        
        self.workout_summaries = self.get_workout_summaries()
        # self.dump_workout_summaries_to_txt(now_str)
        
        self.workout_metrics = self.get_workout_metrics()
        # self.dump_workout_metrics_to_txt(now_str)
        

    def get_workout_list(self) -> list[dict]:
        print('Getting workout list...')
        return self.py_conn.GetWorkoutList()

    def get_workout_ids(self) -> list[str]:
        print('Getting workout IDs...')
        return [workout['id'] for workout in self.workout_list]

    def get_workouts_by_id(self) -> list[dict]:
        print('Getting workouts by ID...')
        return [self.py_conn.GetWorkoutById(workout_id) for workout_id in self.workout_ids]

    def get_workout_summaries(self) -> list[dict]:
        print('Getting workout summaries...')
        return [self.py_conn.GetWorkoutSummaryById(workout_id) for workout_id in self.workout_ids]

    def get_workout_metrics(self) -> list[dict]:
        print('Getting workout metrics...')
        return [self.py_conn.GetWorkoutMetricsById(workout_id) for workout_id in self.workout_ids]

    

    def create_txt_files(self) -> None:
        now_str = datetime.now(tz=EASTERN_TIME).strftime('%Y-%m-%d_%H-%M')
        self.dump_workout_list_to_txt(now_str)
        self.dump_workout_ids_to_txt(now_str)
        self.dump_workouts_by_id_to_txt(now_str)
        self.dump_workout_summaries_to_txt(now_str)
        self.dump_workout_metrics_to_txt(now_str)

    def dump_workout_list_to_txt(self, now_str: str) -> None:
        print('Dumping workout list to TXT...')
        filename = TXT_DIR.joinpath(f"{now_str}_workout_list.txt")
        with open(filename, 'w') as f:
            for i, workout in enumerate(self.workout_list):
                if i == 0:
                    f.write(str(workout))
                else:
                    f.write('\n' + str(workout))

    def dump_workout_ids_to_txt(self, now_str: str) -> None:
        print('Dumping workout IDs to TXT...')
        filename = TXT_DIR.joinpath(f"{now_str}_workout_ids.txt")
        with open(filename, 'w') as f:
            for i, workout_id in enumerate(self.workout_ids):
                if i == 0:
                    f.write(str(workout_id))
                else:
                    f.write('\n' + str(workout_id))

    def dump_workouts_by_id_to_txt(self, now_str: str) -> None:
        print('Dumping workouts by ID to TXT...')
        filename = TXT_DIR.joinpath(f"{now_str}_workouts_by_id.txt")
        with open(filename, 'w') as f:
            # for workout_by_id in self.workouts_by_id:
            #     f.write(str(workout_by_id) + '\n')
            for i, workout_by_id in enumerate(self.workouts_by_id):
                if i == 0:
                    f.write(str(workout_by_id))
                else:
                    f.write('\n' + str(workout_by_id))
            
    def dump_workout_summaries_to_txt(self, now_str: str) -> None:
        print('Dumping workout summaries to TXT...')
        filename = TXT_DIR.joinpath(f"{now_str}_workout_summaries.txt")
        with open(filename, 'w') as f:
            # for workout_summary in self.workout_summaries:
            #     f.write(str(workout_summary) + '\n')
            for i, workout_summary in enumerate(self.workout_summaries):
                if i == 0:
                    f.write(str(workout_summary))
                else:
                    f.write('\n' + str(workout_summary))

    def dump_workout_metrics_to_txt(self, now_str: str) -> None:
        print('Dumping workout metrics to TXT...')
        filename = TXT_DIR.joinpath(f"{now_str}_workout_metrics.txt")
        with open(filename, 'w') as f:
            # for workout_metrics in self.workout_metrics:
            #     f.write(str(workout_metrics) + '\n')
            for i, workout_metrics in enumerate(self.workout_metrics):
                if i == 0:
                    f.write(str(workout_metrics))
                else:
                    f.write('\n' + str(workout_metrics))
                

    def create_csv_files(self) -> None:
        now_str = datetime.now(tz=EASTERN_TIME).strftime('%Y-%m-%d_%H-%M')
        print('Creating CSV files...')
        self.write_workout_list_to_csv(now_str)
        self.write_workout_ids_to_csv(now_str)
        self.write_workouts_by_id_to_csv(now_str)
        self.write_workout_summaries_to_csv(now_str)
        self.write_workout_metrics_to_csv(now_str)

    def write_workout_list_to_csv(self, now_str: str) -> None:
        df = pd.DataFrame(self.workout_list)
        df.to_csv(CSV_DIR.joinpath(f"{now_str}_workout_list.csv"))
        
    def write_workout_ids_to_csv(self, now_str: str) -> None:
        df = pd.DataFrame(self.workout_ids)
        df.to_csv(CSV_DIR.joinpath(f"{now_str}_workout_ids.csv"))
        
    def write_workouts_by_id_to_csv(self, now_str: str) -> None:
        df = pd.DataFrame(self.workouts_by_id)
        df.to_csv(CSV_DIR.joinpath(f"{now_str}_workouts_by_id.csv"))
        
    def write_workout_summaries_to_csv(self, now_str: str) -> None:
        df = pd.DataFrame(self.workout_summaries)
        df.to_csv(CSV_DIR.joinpath(f"{now_str}_workout_summaries.csv"))
        
    def write_workout_metrics_to_csv(self, now_str: str) -> None:
        df = pd.DataFrame(self.workout_metrics)
        df.to_csv(CSV_DIR.joinpath(f"{now_str}_worout_metrics.csv"))





def main():
    pass
    object = PelotonTxtFiles()
    object.get_data_from_peloton()
    object.create_txt_files()
    object.create_csv_files()
    print('Done')


if __name__ == '__main__':
    main()




    # def write_csv_files():
    #     with open('workout_metrics_dump.txt', 'r') as f:
    #         workout_metrics_dict_list = [ast.literal_eval(line) for line in f]
    #     df_metrics = pd.DataFrame(workout_metrics_dict_list)
    #     df_metrics.to_csv('df_metrics.csv')

    #     with open('workout_summary_dump.txt', 'r') as f:
    #         workout_summary_dict_list = [ast.literal_eval(line) for line in f]
    #     df_summary = pd.DataFrame(workout_summary_dict_list)
    #     df_summary.to_csv('df_summary.csv')

    #     with open('workout_by_id_dump.txt', 'r') as f:
    #         workout_by_id_dict_list = [ast.literal_eval(line) for line in f]
    #     df_workouts_by_id = pd.DataFrame(workout_by_id_dict_list)
    #     df_workouts_by_id.to_csv('df_workouts_by_id.csv')
