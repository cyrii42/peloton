import ast
import json
from pprint import pprint

import pandas as pd
import sqlalchemy as db
from pylotoncycle import PylotonCycle

from peloton.constants import PELOTON_PASSWORD, PELOTON_USERNAME

py_conn = PylotonCycle(PELOTON_USERNAME, PELOTON_PASSWORD) 

# total_workouts = py_conn.GetMe()["total_workouts"]

# raw_workout_data = py_conn.GetRecentWorkouts(total_workouts)  # returns a list of dicts

# workout_ids_list = [x for x in raw_workout_data['workout_id'].tolist()]
# workout_metrics_list = [py_conn.GetWorkoutMetricsById(workout_id) for workout_id in workout_ids_list]


# with open('workout_list_dump.txt', 'w') as f:
#     workout_list = py_conn.GetWorkoutList()
#     for workout in workout_list:
#         f.write(str(workout) + '\n')

with open('workout_list_dump.txt', 'r') as f:
    workout_list = [ast.literal_eval(line) for line in f]
    workout_id_list = [workout['id'] for workout in workout_list]

# workout_summary_list = []
# for workout_id in workout_id_list:
#     workout_summary_list.append(py_conn.GetWorkoutSummaryById(workout_id))
# with open('workout_summary_dump.txt', 'w') as f:
#     for workout_summary in workout_summary_list:
#         f.write(str(workout_summary) + '\n')

# workout_by_id_list = []
# for workout_id in workout_id_list:
#     workout_by_id_list.append(py_conn.GetWorkoutById(workout_id))
# with open('workout_by_id_dump.txt', 'w') as f:
#     for workout_by_id in workout_by_id_list:
#         f.write(str(workout_by_id) + '\n')

# workout_metrics_list = []
# for workout_id in workout_id_list:
#     workout_metrics_list.append(py_conn.GetWorkoutMetricsById(workout_id))
# with open('workout_metrics_dump.txt', 'w') as f:
#     for workout_metrics in workout_metrics_list:
#         f.write(str(workout_metrics) + '\n')

with open('workout_metrics_dump.txt', 'r') as f:
    workout_metrics_dict_list = [ast.literal_eval(line) for line in f]
df_metrics = pd.DataFrame(workout_metrics_dict_list)
df_metrics.to_csv('df_metrics.csv')

with open('workout_summary_dump.txt', 'r') as f:
    workout_summary_dict_list = [ast.literal_eval(line) for line in f]
df_summary = pd.DataFrame(workout_summary_dict_list)
df_summary.to_csv('df_summary.csv')

with open('workout_by_id_dump.txt', 'r') as f:
    workout_by_id_dict_list = [ast.literal_eval(line) for line in f]
df_workouts_by_id = pd.DataFrame(workout_by_id_dict_list)
df_workouts_by_id.to_csv('df_workouts_by_id.csv')