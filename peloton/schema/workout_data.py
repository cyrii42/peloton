import ast
import json
from datetime import datetime

import pandas as pd
from pydantic import (BaseModel, ConfigDict, Field, computed_field,
                      field_validator)

from peloton.constants import DF_DTYPES_DICT, WORKOUTS_DIR, EASTERN_TIME
from peloton.exceptions import WorkoutMismatchError

from .metrics import PelotonMetrics
from .summary import PelotonSummary


class PelotonWorkoutData(BaseModel):
    model_config = ConfigDict(frozen=True)
    workout_id: str
    summary_raw: dict = Field(repr=False)
    metrics_raw: dict = Field(repr=False)
    summary: PelotonSummary
    metrics: PelotonMetrics

    @field_validator('workout_id')
    @classmethod
    def workout_id_is_UUID_not_all_zeroes(cls, workout_id: str) -> str:
        if workout_id is None or len(workout_id) != 32 or workout_id.count('0') == 32:
            raise ValueError("invalid Workout ID")
        else:
            return workout_id

    @computed_field
    def output_per_min(self) -> float | None:
        if (self.metrics.summaries is None 
                or self.summary.ride.ride_duration is None
                or self.summary.ride.ride_duration == 0):
            return None

        total_output = None
        for unit in self.metrics.summaries:
            if unit.slug == 'total_output':
                total_output = unit.value
        if total_output is None:
            return None

        ride_minutes = (self.summary.ride.ride_duration / 60)

        return (total_output / ride_minutes)

    @computed_field
    def duration_hrs(self) -> float | None:
        if self.summary.ride.ride_duration is None or self.summary.ride.ride_duration == 0:
            return None

        return (self.summary.ride.ride_duration / 3600)

                

    def create_dataframe(self) -> pd.DataFrame:
        # print(f"Making dataframe for workout {self.workout_id} at {datetime.now(tz=EASTERN_TIME)}...")
        output_dict = {}
        
        summary_dict = self.summary.model_dump()
        ride_dict = summary_dict.pop('ride')
        output_dict.update(summary_dict)
        output_dict.update(ride_dict)

        metrics_summaries_dict_list = [x.model_dump() for x in self.metrics.summaries]
        metrics_summaries_dict_list = [{d['slug']: d['value']} for d in metrics_summaries_dict_list]
        combined_dict = {key: value for d in metrics_summaries_dict_list for key, value in d.items()}
        output_dict.update(combined_dict)

        metrics_metrics_dict_list = [x.model_dump() for x in self.metrics.metrics]
        metrics_metrics_dict_list = ([{f"avg_{d['slug']}": d['average_value']} for d in metrics_metrics_dict_list] 
                                       + [{f"max_{d['slug']}": d['max_value']} for d in metrics_metrics_dict_list])
        combined_dict = {key: value for d in metrics_metrics_dict_list for key, value in d.items()}
        output_dict.update(combined_dict)

        metrics_hr_zones_dict_list = [x.model_dump() for x in self.metrics.metrics]
        metrics_hr_zones_dict_list = [d['zones'] for d in metrics_hr_zones_dict_list if d['zones'] is not None]
        if len(metrics_hr_zones_dict_list) > 0:
            metrics_hr_zones_dict_list = [{f"hr_{d['slug']}": d['duration']} for d in metrics_hr_zones_dict_list[0]]
            combined_dict = {key: value for d in metrics_hr_zones_dict_list for key, value in d.items()}
            output_dict.update(combined_dict)
  
        if self.metrics.effort_zones is not None:
            metrics_effort_zones_dict = self.metrics.effort_zones.model_dump()
            output_dict.update(metrics_effort_zones_dict)

        output_dict.update({'output_per_min': self.output_per_min, 'duration_hrs': self.duration_hrs})

        return pd.DataFrame([output_dict]).dropna(axis='columns', how='all')

def test_import() -> list[PelotonWorkoutData]:
    with open('../../data/workout_ids.txt', 'r') as f:
        workout_id_list = [line.rstrip('\n') for line in f.readlines()]
    with open('../../data/workout_summaries.txt', 'r') as f:
        summary_list = [ast.literal_eval(line) for line in f.readlines()]
    with open('../../data/workout_metrics.txt', 'r') as f:
        metrics_list = [ast.literal_eval(line) for line in f.readlines()]

    if len(workout_id_list) == len(summary_list) and len(workout_id_list) == len(metrics_list):
        num_workouts = len(workout_id_list)
    else:
        raise WorkoutMismatchError('TXT files with workout IDs, summaries, and metrics are not all the same length!')

    output_list=[]
    for i in range(num_workouts):
        workout_data = PelotonWorkoutData(
            workout_id=workout_id_list[i],
            summary_raw=summary_list[i],
            metrics_raw=metrics_list[i],
            summary=PelotonSummary(**summary_list[i]),
            metrics=PelotonMetrics(**metrics_list[i])
        )
        output_list.append(workout_data)

    return output_list

def write_workouts_to_disk(workouts: list[PelotonWorkoutData]) -> None:
    for workout in workouts:
        with open(WORKOUTS_DIR.joinpath(f"{workout.workout_id}.json"), 'w') as f:
            json.dump(workout.model_dump(), f, indent=4)


def main():
    workouts = test_import()
    # print(workouts[175].create_dataframe())

    df = pd.concat([workout.create_dataframe() for workout in workouts], ignore_index=True)
    print(df.tail(40))
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