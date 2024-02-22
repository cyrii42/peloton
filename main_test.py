import ast
import json
from pathlib import Path
from pprint import pprint

import pandas as pd
import sqlalchemy as db
from pydantic import BaseModel
from typing_extensions import Any

from peloton import (BASE_URL, EASTERN_TIME, INSTRUCTORS_JSON, SESSION_JSON,
                     SQLITE_FILENAME, WORKOUTS_DIR, PelotonProcessorNew)

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

# def create_dtypes_dict(input: BaseModel | list[BaseModel], output_dict: dict = dict()):
#         output_dict = dict()

#         if isinstance(input, BaseModel):
#             for name, value in input:
#                 if isinstance(value, BaseModel | list):
#                     return create_dtypes_dict(value, output_dict=output_dict)
#                 else:
#                     output_dict.update({name: type(value)})

#         elif isinstance(input, list):
#             for item in input:
#                 return create_dtypes_dict(value, output_dict=output_dict)
                
#         else: 
#             output_dict.update({name: type(value)})
                    
#         return output_dict



def main():
    sql_engine = db.create_engine(SQLITE_FILENAME)
    processor = PelotonProcessorNew(sql_engine)
    # processor.check_for_new_workouts()
    # print(processor.json_writer.all_workouts[34])
    df = processor.processed_df
    print(df)
    # print(df.info())
    df.to_csv('testtesddddasdfasdfddddssdt.csv')

    # m = processor.json_writer.all_workouts[42]
    
    # print(m.create_dataframe().info())

    
    # print(processor.processed_df.info())
    
    # workouts = test_import()
    # print(workouts)
    # # print(workouts[175].create_dataframe())

    # df = pd.concat([workout.create_dataframe() for workout in workouts], ignore_index=True)
    # print(df.tail(40))
    # print(df[df['duration'].isna() == False])

    # sql_writer = PelotonSQL(db.create_engine(SQLITE_FILENAME))
    # sql_writer.export_data_to_sql(df, 'peloton_test')

    # write_workouts_to_disk(workouts)

    # workout_list = [workout.create_dataframe() for workout in test_import()]
    # all_workouts = pd.concat(workout_list, ignore_index=True)
    # print(all_workouts.iloc[134].to_dict())
    # all_workouts.to_csv('all_workouts_test.csv')


if __name__ == '__main__':
    main()