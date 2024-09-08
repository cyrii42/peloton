import ast
import json
from datetime import datetime
from pathlib import Path
from pprint import pprint
from typing import Union
from zoneinfo import ZoneInfo

import pandas as pd
import requests
import sqlalchemy as db
from pydantic import (AliasChoices, BaseModel, ConfigDict, Field,
                      ValidationError, computed_field, field_serializer,
                      field_validator)
# from pyloton_zmv import PylotonZMV
# from peloton_instructors import PelotonHumanInstructor, PelotonNonHumanInstructor, get_instructor_by_id
from sqlalchemy.orm import declarative_base
from typing_extensions import List, Optional
# from peloton_sql import PelotonSQL
from ..peloton.helpers.exceptions import PelotonInstructorNotFoundError, WorkoutMismatchError

BASE_URL = "https://api.onepeloton.com"
EASTERN_TIME = ZoneInfo('America/New_York')
INSTRUCTORS_JSON = Path('..').resolve().joinpath('peloton_instructors.json')
WORKOUTS_DIR = Path('..').resolve().joinpath('data', 'workouts')
SQLITE_FILENAME = "sqlite:///../data/peloton.db"

class PelotonHumanInstructor(BaseModel):
    model_config = ConfigDict(frozen=True)
    instructor_id: str = Field(alias=AliasChoices('ride_instructor_id', 'instructor_id', 'id'))
    first_name: str
    last_name: str
    about_image_url: str
    background: str
    bio: str
    fitness_disciplines: List[str]
    image_url: str
    instagram_profile: str
    instructor_hero_image_url: str
    ios_instructor_list_display_image_url: str
    jumbotron_url_dark: str
    jumbotron_url_ios: str
    life_style_image_url: str
    ordered_q_and_as: List[List[str]]
    quote: str
    short_bio: str
    spotify_playlist_uri: str
    strava_profile: str
    twitter_profile: str
    username: str
    web_instructor_list_display_image_url: str

    @computed_field
    def full_name(self) -> str:
        return self.first_name + ' ' + self.last_name

    @field_validator('instructor_id')
    @classmethod
    def instructor_id_is_UUID_not_all_zeroes(cls, instructor_id: str) -> str:
        if instructor_id is None or len(instructor_id) != 32 or instructor_id.count('0') == 32:
            return None
        else:
            return instructor_id

class PelotonNonHumanInstructor(BaseModel):
    ''' With human instructors, the `instructor` field is empty in the `ride` column, but with 
    "JUST RIDE" or "LANEBREAK" or "ENTERTAINMENT" rides, it's not:
    
    `'instructor': {'name': 'JUST RIDE',
    'image_url': 'https://s3.amazonaws.com/peloton-ride-images/just-ride-indoor.png'}`'''
    
    name: str
    image_url: str

# def get_instructor_by_id(instructor_id: str) -> PelotonHumanInstructor | None:
#     try:
#         with open(INSTRUCTORS_JSON, 'r') as f:
#             instructors_dict = json.load(f)
#     except FileNotFoundError:
#         instructors_dict = dict()
        
#     if instructor_id in instructors_dict.keys():
#         return PelotonHumanInstructor.model_validate(instructors_dict[instructor_id])
    
#     else:
#         url = f"{BASE_URL}/api/instructor/{instructor_id}"
#         try:
#             py_conn = PylotonZMV()
#             resp = py_conn.session.get(url, timeout=10)
#             resp.raise_for_status()
#         except requests.HTTPError:
#             if resp.status_code == 401:
#                 py_conn.get_new_login_token()
#                 resp = py_conn.session.get(url, timeout=10)
#                 resp.raise_for_status()
#             elif resp.status_code == 404:
#                 raise PelotonInstructorNotFoundError(f"Instructor ID '{instructor_id}' not found.")
#             else:
#                 raise requests.HTTPError
            
#         try:
#             instructor = PelotonHumanInstructor.model_validate(resp.json())
#             instructors_dict.update({instructor.instructor_id: instructor.model_dump()})
#             with open(INSTRUCTORS_JSON, 'w') as f:
#                 json.dump(instructors_dict, f, indent=4)
#                 return instructor
#         except ValidationError as e:
#             print(e)
#             return None





class PelotonRideColumn(BaseModel):
    model_config = ConfigDict(frozen=True)
    title: Optional[str] = None
    description: Optional[str] = None
    ride_duration: Optional[int] = Field(alias='duration', default=None)
    ride_length: Optional[int] = Field(alias='length', default=None)
    image_url: Optional[str] = None
    difficulty_estimate: Optional[float] = None
    # fitness_discipline: Optional[str] = None
    # ride_id: Optional[str] = Field(alias=AliasChoices('id', 'ride_id'), default=None)
    instructor_json: Optional[PelotonNonHumanInstructor] = Field(alias='instructor', default=None)
    instructor_id: Optional[str] = Field(alias=AliasChoices('instructor_id'), default=None)
    
    

    @field_validator('instructor_id')
    @classmethod
    def instructor_id_is_UUID_not_all_zeroes(cls, instructor_id: str) -> str:
        if instructor_id is None or len(instructor_id) != 32 or instructor_id.count('0') == 32:
            return None
        else:
            return instructor_id
        
    @computed_field
    def instructor_name(self) -> str | None:
        if self.instructor_id is not None:
            try:
                with open(INSTRUCTORS_JSON, 'r') as f:
                    instructors_dict = json.load(f)
                if self.instructor_id in instructors_dict.keys():
                    instructor_data = instructors_dict[self.instructor_id]
                    instructor = PelotonHumanInstructor.model_validate(instructor_data)
                    return instructor.full_name
            except FileNotFoundError:
                self.get_instructor_from_peloton()
        elif self.instructor_json is not None:
            return self.instructor_json.name
        else:
            return None

    def get_instructor_from_peloton(self) -> PelotonHumanInstructor | None:
        if self.instructor_id is not None:
            try:
                py_conn = PylotonZMV()
                instructor_data = py_conn.get_instructor_by_id(self.instructor_id, skip_json=True)
                instructor = PelotonHumanInstructor.model_validate(instructor_data)
                return instructor
            except PelotonInstructorNotFoundError or requests.HTTPError:
                return None
        else:
            return None
        

class PelotonSummary(BaseModel):
    model_config = ConfigDict(frozen=True)
    workout_id: str
    start_time: Union[int, datetime, str]
    end_time: Union[int, datetime, str]
    metrics_type: str
    workout_type: str
    leaderboard_rank: Optional[Union[int, float]] = None
    total_leaderboard_users: Optional[int] = None
    average_effort_score: Optional[float] = None
    ride: PelotonRideColumn

    #### CALCULATE LEADERBOARD PERCENTILE??? ####

    @field_validator('workout_id')
    @classmethod
    def workout_id_is_UUID_not_all_zeroes(cls, workout_id: str) -> str:
        if workout_id is None or len(workout_id) != 32 or workout_id.count('0') == 32:
            raise ValueError("invalid Workout ID")
        else:
            return workout_id

    @field_validator('start_time', 'end_time')
    @classmethod
    def convert_timestamp(cls, ts: Union[int, str]) -> datetime:
        if isinstance(ts, int):
            return datetime.fromtimestamp(ts, tz=EASTERN_TIME)
        elif isinstance(ts, str):
            return datetime.fromisoformat(ts).astimezone(tz=EASTERN_TIME)

    @field_serializer('start_time', 'end_time', when_used='always')
    def convert_datetime_to_string(dt: datetime) -> str:
        return dt.isoformat(sep='T', timespec='seconds')






class PelotonMetricsEffortZoneSummary (BaseModel):
    model_config = ConfigDict(frozen=True)
    display_name: str
    duration: int
    max_value: Union[int, float]
    min_value: Union[int, float]
    range: str
    slug: str

class PelotonMetricsUnitSummary(BaseModel):
    model_config = ConfigDict(frozen=True)
    average_value: Optional[Union[int, float]] = None
    display_name: str
    display_unit: str
    max_value: Optional[Union[int, float]] = None
    slug: str
    values: Optional[List[Union[int, float]]] = None
    zones: Optional[List[PelotonMetricsEffortZoneSummary]] = None

class PelotonMetricsTotals(BaseModel):
    model_config = ConfigDict(frozen=True)
    display_name: str
    display_unit: str
    slug: str
    value: Optional[Union[int, float]] = None

class PelotonMetrics(BaseModel):
    model_config = ConfigDict(frozen=True)
    workout_id: str
    metrics: List[PelotonMetricsUnitSummary]
    summaries: List[PelotonMetricsTotals]

    @field_validator('workout_id')
    @classmethod
    def workout_id_is_UUID_not_all_zeroes(cls, workout_id: str) -> str:
        if workout_id is None or len(workout_id) != 32 or workout_id.count('0') == 32:
            raise ValueError("invalid Workout ID")
        else:
            return workout_id






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

    def create_dataframe(self) -> pd.DataFrame:
        # summary_df = pd.json_normalize(self.summary.model_dump())
        summary_dict = self.summary.model_dump()
        ride_dict = summary_dict.pop('ride')
        summary_df = pd.DataFrame([summary_dict])
        ride_df = pd.DataFrame([ride_dict])

        metrics_summaries_dict_list = [x.model_dump() for x in self.metrics.summaries]
        metrics_summaries_dict_list = [{d['slug']: d['value']} for d in metrics_summaries_dict_list]
        combined_dict = {key: value for d in metrics_summaries_dict_list for key, value in d.items()}
        metrics_summaries_df = pd.DataFrame([combined_dict])

        metrics_metrics_dict_list = [x.model_dump() for x in self.metrics.metrics]
        metrics_metrics_dict_list = ([{f"avg_{d['slug']}": d['average_value']} for d in metrics_metrics_dict_list] 
                                       + [{f"max_{d['slug']}": d['max_value']} for d in metrics_metrics_dict_list])
        combined_dict = {key: value for d in metrics_metrics_dict_list for key, value in d.items()}
        metrics_metrics_df = pd.DataFrame([combined_dict])

        metrics_hr_zones_dict_list = [x.model_dump() for x in self.metrics.metrics]
        metrics_hr_zones_dict_list = [d['zones'] for d in metrics_hr_zones_dict_list if d['zones'] is not None]
        if len(metrics_hr_zones_dict_list) == 0:
            metrics_hr_zones_df = pd.DataFrame()
        else:
            metrics_hr_zones_dict_list = [{f"hr_{d['slug']}": d['duration']} for d in metrics_hr_zones_dict_list[0]]
            combined_dict = {key: value for d in metrics_hr_zones_dict_list for key, value in d.items()}
            metrics_hr_zones_df = pd.DataFrame([combined_dict])

        return (pd.concat([summary_df, ride_df, metrics_metrics_df, 
                           metrics_summaries_df, metrics_hr_zones_df],
                        axis=1).dropna(axis='columns', how='all'))




def test_import() -> list[PelotonWorkoutData]:
    with open('../data/workout_ids.txt', 'r') as f:
        workout_id_list = [line.rstrip('\n') for line in f.readlines()]
    with open('../data/workout_summaries.txt', 'r') as f:
        summary_list = [ast.literal_eval(line) for line in f.readlines()]
    with open('../data/workout_metrics.txt', 'r') as f:
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
            summary=PelotonSummary.model_validate(summary_list[i]),
            metrics=PelotonMetrics.model_validate(metrics_list[i])
        )
        output_list.append(workout_data)

    return output_list

def write_workouts_to_disk(workouts: list[PelotonWorkoutData]) -> None:
    for workout in workouts:
        with open(WORKOUTS_DIR.joinpath(f"{workout.workout_id}.json"), 'w') as f:
            json.dump(workout.model_dump(), f, indent=4)


def main():
    pass
    # workouts = test_import()
    # print(workouts[175].create_dataframe())

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