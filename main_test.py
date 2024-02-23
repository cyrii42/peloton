import ast
import json
from pathlib import Path
from pprint import pprint

import pandas as pd
import sqlalchemy as db

from peloton import SQLITE_FILENAME, PelotonProcessor

# def test_import() -> list[PelotonWorkoutData]:
#     with open('./data/workout_ids.txt', 'r') as f:
#         workout_id_list = [line.rstrip('\n') for line in f.readlines()]
#     with open('./data/workout_summaries.txt', 'r') as f:
#         summary_list = [ast.literal_eval(line) for line in f.readlines()]
#     with open('./data/workout_metrics.txt', 'r') as f:
#         metrics_list = [ast.literal_eval(line) for line in f.readlines()]

#     if len(workout_id_list) == len(summary_list) and len(workout_id_list) == len(metrics_list):
#         num_workouts = len(workout_id_list)
#     else:
#         raise WorkoutMismatchError('TXT files with workout IDs, summaries, and metrics are not all the same length!')

#     output_list=[]
#     for i in range(num_workouts):
#         workout_data = PelotonWorkoutData(
#             workout_id=workout_id_list[i],
#             summary_raw=summary_list[i],
#             metrics_raw=metrics_list[i],
#             summary=PelotonSummary.model_validate(summary_list[i]),
#             metrics=PelotonMetrics.model_validate(metrics_list[i])
#         )
#         output_list.append(workout_data)

#     return output_list

# def write_workouts_to_disk(workouts: list[PelotonWorkoutData]) -> None:
#     for workout in workouts:
#         with open(WORKOUTS_DIR.joinpath(f"{workout.workout_id}.json"), 'w') as f:
#             json.dump(workout.model_dump(), f, indent=4)




def main():
    sql_engine = db.create_engine(SQLITE_FILENAME)
    processor = PelotonProcessor(sql_engine)
    # processor.check_for_new_workouts()
    print(processor.processed_df)
    print(processor.pivots.year_table)
    print(processor.pivots.month_table)
    print(processor.pivots.totals_table)

    # df = processor.processed_df
    # print(df)
    # # print(df.info())
    # df.to_csv('testtesddddasdfasdfddddssdt.csv')


    # processor.reprocess_json_data()

if __name__ == '__main__':
    main()