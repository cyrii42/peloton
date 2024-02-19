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
from pyloton_connector import PylotonZMVConnector
from sqlalchemy.orm import declarative_base
from typing_extensions import List, Optional

BASE_URL = "https://api.onepeloton.com"
EASTERN_TIME = ZoneInfo('America/New_York')
INSTRUCTORS_JSON = Path('..').resolve().joinpath('peloton_instructors.json')
WORKOUTS_DIR = Path('..').resolve().joinpath('data', 'workouts')


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






class PelotonRideColumn(BaseModel):
    model_config = ConfigDict(frozen=True)
    description: str = None #Field(alias='description', default=None)
    difficulty_estimate: float = None #Field(alias='difficulty_estimate', default=None)
    duration: int = None #Field(alias='duration')
    fitness_discipline: str = None #Field(alias='fitness_discipline', default=None)
    ride_id: str = Field(alias='id')
    image_url: str = None #Field(alias='image_url', default=None)
    instructor_json: Optional[PelotonNonHumanInstructor] = Field(alias='instructor', default=None)
    instructor_id: Optional[str] = Field(alias=AliasChoices('instructor_id', 'id'), default=None)
    length: int = None #Field(alias='length', default=None)
    title: str = None #Field(alias='title')

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
                return get_instructor_by_id(self.instructor_id).full_name
            except PelotonInstructorNotFoundError as e:
                print(e)
                return None
        elif self.instructor_json is not None:
            return self.instructor_json.name
        else:
            return None

class PelotonSummary(BaseModel):
    model_config = ConfigDict(frozen=True)
    workout_id: str
    average_effort_score: Optional[float] = None
    end_time: Union[int, datetime]
    leaderboard_rank: Optional[Union[int, float]] = None
    metrics_type: str
    name: str
    start_time: Union[int, datetime]
    timezone: Optional[str] = None
    total_leaderboard_users: Optional[int] = None
    total_work: float
    user_id: str
    workout_type: str
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
    def convert_timestamp(cls, ts: int) -> datetime:
        return datetime.fromtimestamp(ts, tz=EASTERN_TIME)

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
    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)
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
    def summary_df(self) -> pd.DataFrame:
        return pd.json_normalize(self.summary.model_dump())

    @computed_field
    def metrics_summary_df(self) -> pd.DataFrame:
        metrics_summaries = self.metrics.summaries
        dict_list = [x.model_dump() for x in metrics_summaries]
        dict_list = [{d['slug']: d['value']} for d in dict_list]
        combined_dict = {key: value for d in dict_list for key, value in d.items()}
        return pd.DataFrame([combined_dict])

    @computed_field
    def metrics_metrics_df(self) -> pd.DataFrame:
        metrics_metrics = self.metrics.metrics
        dict_list = [x.model_dump() for x in metrics_metrics]
        dict_list = ([{f"avg_{d['slug']}": d['average_value']} for d in dict_list] 
                       + [{f"max_{d['slug']}": d['max_value']} for d in dict_list])
        combined_dict = {key: value for d in dict_list for key, value in d.items()}
        return pd.DataFrame([combined_dict])

    @computed_field
    def metrics_hr_zones_df(self) -> pd.DataFrame:
        metrics_metrics = self.metrics.metrics
        dict_list = [x.model_dump() for x in metrics_metrics]
        dict_list = [d['zones'] for d in dict_list if d['zones'] is not None]
        if len(dict_list) == 0:
            return pd.DataFrame()
        else:
            dict_list = [{f"hr_{d['slug']}": d['duration']} for d in dict_list[0]]
            combined_dict = {key: value for d in dict_list for key, value in d.items()}
            return pd.DataFrame([combined_dict])

    @computed_field
    def full_df(self) -> pd.DataFrame:
        return pd.concat([self.summary_df, self.metrics_metrics_df,  
                          self.metrics_summary_df,self.metrics_hr_zones_df], axis=1).dropna(axis='columns', how='all')






def get_instructor_by_id(instructor_id: str) -> PelotonHumanInstructor | None:
    try:
        with open(INSTRUCTORS_JSON, 'r') as f:
            instructors_dict = json.load(f)
    except FileNotFoundError:
        instructors_dict = dict()
    if instructor_id in instructors_dict.keys():
        # print(f"Found {instructors_dict[instructor_id]['full_name']} in dictionary!")
        return PelotonHumanInstructor.model_validate(instructors_dict[instructor_id])
    
    url = f"{BASE_URL}/api/instructor/{instructor_id}"
    try:
        pyloton = PylotonZMVConnector()
        resp = pyloton.session.get(url, timeout=10)
        resp.raise_for_status()
    except requests.HTTPError:
        if resp.status_code == 401:
            pyloton.get_new_login_token()
            resp = pyloton.session.get(url, timeout=10)
            resp.raise_for_status()
        elif resp.status_code == 404:
            raise PelotonInstructorNotFoundError(f"Instructor ID '{instructor_id}' not found.")
        else:
            raise requests.HTTPError
    try:
        instructor = PelotonHumanInstructor.model_validate(resp.json())
        instructors_dict.update({instructor_id: instructor.model_dump()})
        with open(INSTRUCTORS_JSON, 'w') as f:
            json.dump(instructors_dict, f)
        return instructor
    except ValidationError as e:
        print(e)
        return None




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
            json.dump(workout.model_dump(), f)
    
class PelotonInstructorNotFoundError(Exception):
    pass

class WorkoutMismatchError(Exception):
    pass


def main():
    # workout = test_import()[186]

    # print(workout.full_df)

    workout_list = [workout.full_df for workout in test_import()]
    all_workouts = pd.concat(workout_list, ignore_index=True)
    all_workouts.to_csv('all_workouts_test.csv')

if __name__ == '__main__':
    main()