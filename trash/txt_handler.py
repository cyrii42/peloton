# import ast
# import json
# from datetime import datetime
# from pathlib import Path
# from pprint import pprint


# import pandas as pd
# from peloton.schema import PelotonWorkoutData
# import sqlalchemy as db
# from peloton.constants import PELOTON_PASSWORD, PELOTON_USERNAME, EASTERN_TIME
# from peloton.exceptions import WorkoutMismatchError


# TXT_DIR = Path('/home/zvaughan/python/peloton/data/raw_txt').resolve()
# CSV_DIR = Path('/home/zvaughan/python/peloton/data/raw_csv').resolve()


# class PelotonTxtFiles():
#     def __init__(self):
#         self.pyloton = PylotonZMV(PELOTON_USERNAME, PELOTON_PASSWORD) 
#         try:
#             self.total_workouts_on_disk = self.count_workouts()
#         except FileNotFoundError or WorkoutMismatchError:
#             print('ERROR: re-starting at 0 workouts...')
#             self.total_workouts_on_disk = 0
            
#         if self.total_workouts_on_disk > 0:
#             self.workout_ids = self.get_workout_ids_from_txt()
#             self.workout_summaries = self.get_workout_summaries_from_txt()
#             self.workout_metrics = self.get_workout_metrics_from_txt()
#         else:
#             self.workout_ids = self.workout_summaries = self.workout_metrics = None


#     def populate_models_from_txt(self):
#         for test_metric in self.workout_metrics:
#             test_metric = PelotonMetrics.model_validate(test_metric)
#             print(test_metric)
#         for test_summary in self.workout_summaries:
#             test_summary = PelotonSummary.model_validate(test_summary)
#             print(test_summary)
        
#     def test_json_dump(self):
#         test_metrics = self.workout_metrics[234]
#         model1 = PelotonMetrics.model_validate(test_metrics)
#         print(model1.model_dump_json(indent=2))
#         test_summary = self.workout_summaries[234]
#         model2 = PelotonSummary.model_validate(test_summary)
#         print(model2.model_dump_json(indent=2))


#     def count_workouts(self) -> int:
#         with open('../data/workout_ids.txt', 'r') as f:
#             num_ids = len(f.readlines())
#         with open('../data/workout_summaries.txt', 'r') as f:
#             num_summaries = len(f.readlines())
#         with open('../data/workout_metrics.txt', 'r') as f:
#             num_metrics = len(f.readlines())

#         if num_ids == num_summaries and num_ids == num_metrics:
#             return num_ids
#         else:
#             raise WorkoutMismatchError

#     def get_workout_ids_from_txt(self) -> list[str]:
#         ''' Retrives workout IDs from TXT file and returns them in reverse-chron order. '''
#         with open('../data/workout_ids.txt', 'r') as f:
#             line_list = f.readlines()
#         return [line.rstrip('\n') for line in line_list]

#     def get_workout_summaries_from_txt(self) -> list[dict]:
#         ''' Retrives workout summaries from TXT file and returns them in reverse-chron order. '''
#         with open('../data/workout_summaries.txt', 'r') as f:
#             line_list = f.readlines()
#         return [ast.literal_eval(line) for line in line_list]

#     def get_workout_summary_rides_from_txt(self) -> list[dict]:
#         ''' Retrives the "RIDE" workout-summary column from TXT file and returns them in reverse-chron order. '''
#         with open('../data/workout_summaries.txt', 'r') as f:
#             line_list = f.readlines()
#         return [ast.literal_eval(line)['ride'] for line in line_list]

#     def get_workout_metrics_from_txt(self) -> list[dict]:
#         ''' Retrives workout metrics from TXT file and returns them in reverse-chron order. '''
#         with open('../data/workout_metrics.txt', 'r') as f:
#             line_list = f.readlines()
#         return [ast.literal_eval(line) for line in line_list]

    

#     def get_data_from_peloton(self) -> None:        
#         self.workout_ids = self.get_workout_ids_from_peloton()        
#         self.workout_summaries = self.get_workout_summaries_from_peloton()        
#         self.workout_metrics = self.get_workout_metrics_from_peloton()
                
#     def get_workout_ids_from_peloton(self) -> list[str]:
#         print('Getting workout IDs...')
#         return self.pyloton.get_workout_ids()

#     def get_workout_summaries_from_peloton(self) -> list[dict]:
#         print('Getting workout summaries...')
#         return [self.pyloton.get_workout_summary_by_id(workout_id) for workout_id in self.workout_ids]

#     def get_workout_metrics_from_peloton(self) -> list[dict]:
#         print('Getting workout metrics...')
#         return [self.pyloton.get_workout_metrics_by_id(workout_id) for workout_id in self.workout_ids]

    

#     def create_txt_files(self) -> None:
#         now_str = datetime.now(tz=EASTERN_TIME).strftime('%Y-%m-%d_%H-%M')
#         self.dump_workout_ids_to_txt(now_str)
#         self.dump_workout_summaries_to_txt(now_str)
#         self.dump_workout_metrics_to_txt(now_str)

#     def dump_workout_ids_to_txt(self, now_str: str) -> None:
#         print('Dumping workout IDs to TXT...')
#         filename = TXT_DIR.joinpath(f"{now_str}_workout_ids.txt")
#         with open(filename, 'w') as f:
#             for i, workout_id in enumerate(self.workout_ids):
#                 if i == 0:
#                     f.write(str(workout_id))
#                 else:
#                     f.write('\n' + str(workout_id))
            
#     def dump_workout_summaries_to_txt(self, now_str: str) -> None:
#         print('Dumping workout summaries to TXT...')
#         filename = TXT_DIR.joinpath(f"{now_str}_workout_summaries.txt")
#         with open(filename, 'w') as f:
#             # for workout_summary in self.workout_summaries:
#             #     f.write(str(workout_summary) + '\n')
#             for i, workout_summary in enumerate(self.workout_summaries):
#                 if i == 0:
#                     f.write(str(workout_summary))
#                 else:
#                     f.write('\n' + str(workout_summary))

#     def dump_workout_metrics_to_txt(self, now_str: str) -> None:
#         print('Dumping workout metrics to TXT...')
#         filename = TXT_DIR.joinpath(f"{now_str}_workout_metrics.txt")
#         with open(filename, 'w') as f:
#             # for workout_metrics in self.workout_metrics:
#             #     f.write(str(workout_metrics) + '\n')
#             for i, workout_metrics in enumerate(self.workout_metrics):
#                 if i == 0:
#                     f.write(str(workout_metrics))
#                 else:
#                     f.write('\n' + str(workout_metrics))
                

#     def create_csv_files(self) -> None:
#         now_str = datetime.now(tz=EASTERN_TIME).strftime('%Y-%m-%d_%H-%M')
#         print('Creating CSV files...')
#         self.write_workout_ids_to_csv(now_str)
#         self.write_workout_summaries_to_csv(now_str)
#         self.write_workout_metrics_to_csv(now_str)
       
#     def write_workout_ids_to_csv(self, now_str: str) -> None:
#         df = pd.DataFrame(self.workout_ids)
#         df.to_csv(CSV_DIR.joinpath(f"{now_str}_workout_ids.csv"))
       
#     def write_workout_summaries_to_csv(self, now_str: str) -> None:
#         df = pd.DataFrame(self.workout_summaries)
#         df.to_csv(CSV_DIR.joinpath(f"{now_str}_workout_summaries.csv"))
        
#     def write_workout_metrics_to_csv(self, now_str: str) -> None:
#         df = pd.DataFrame(self.workout_metrics)
#         df.to_csv(CSV_DIR.joinpath(f"{now_str}_worout_metrics.csv"))





# def main():
#     pass
#     object = PelotonTxtFiles()
#     # object.populate_models_from_txt()
#     object.test_json_dump()



# if __name__ == '__main__':
#     main()
