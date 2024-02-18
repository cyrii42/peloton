import ast
from datetime import datetime, timedelta
from pprint import pprint
from typing import Union
from uuid import UUID
from zoneinfo import ZoneInfo

import sqlalchemy as db
from pydantic import (BaseModel, ConfigDict, Field, computed_field,
                      field_serializer, field_validator)
from peloton_instructors import PelotonInstructorFinder, PelotonInstructorNotFoundError
from sqlalchemy.orm import declarative_base
from typing_extensions import List, Optional

EASTERN_TIME = ZoneInfo('America/New_York')

class WorkoutMismatchError(Exception):
    pass

class PelotonRawMetrics(BaseModel):
    model_config = ConfigDict(frozen=True)
    data: dict

class PelotonRawSummary(BaseModel):
    model_config = ConfigDict(frozen=True)
    data: dict

class PelotonInstructor(BaseModel):
    model_config = ConfigDict(frozen=True)
    instructor_id: UUID = Field(alias='id')
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

    @field_serializer('instructor_id', when_used='always')
    def convert_uuid(uuid: UUID) -> str:
        return str(uuid)



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

class PelotonNonHumanInstructor(BaseModel):
    ''' With human instructors, the `instructor` field is empty in the `ride` column, but with 
    "JUST RIDE" or "LANEBREAK" or "ENTERTAINMENT" rides, it's not:
    
    `'instructor': {'name': 'JUST RIDE',
    'image_url': 'https://s3.amazonaws.com/peloton-ride-images/just-ride-indoor.png'}`'''
    
    name: str
    image_url: str

class PelotonRideColumn(BaseModel):
    model_config = ConfigDict(frozen=True)
    ride_description: str = Field(alias='description', default=None)
    ride_difficulty_estimate: float = Field(alias='difficulty_estimate', default=None)
    ride_duration: int = Field(alias='duration')
    ride_fitness_discipline: str = Field(alias='fitness_discipline', default=None)
    ride_id: UUID = Field(alias='id')
    ride_image_url: str = Field(alias='image_url', default=None)
    ride_instructor_json: Optional[PelotonNonHumanInstructor] = Field(alias='instructor', default=None)
    ride_instructor_id: Optional[str] = Field(alias='instructor_id', default=None)
    ride_length: int = Field(alias='length', default=None)
    ride_title: str = Field(alias='title')

    ###### STILL NEED TO IMPLEMENT SOME METHOD FOR GETTING REAL INSTRUCTOR NAMES FROM INSTRUCTOR IDs #####

    @computed_field
    def ride_instructor_name(self) -> str | None:
        if self.ride_instructor_json is not None:
            return self.ride_instructor_json.name
        elif self.ride_instructor_id is not None:
            try:
                PelotonInstructorFinder.get_instructor_by_id(self.ride_instructor_id)
            except PelotonInstructorNotFoundError as e:
                print(e)
                return None
        else:
            return None

    @field_serializer('ride_id', when_used='always')
    def convert_uuid(uuid: UUID) -> str:
        return str(uuid)

class PelotonMetrics(BaseModel):
    model_config = ConfigDict(frozen=True)
    workout_id: UUID
    metrics: List[PelotonMetricsUnitSummary]
    summaries: List[PelotonMetricsTotals]

    @field_serializer('workout_id', when_used='always')
    def convert_uuid(uuid: UUID) -> str:
        return str(uuid)

class PelotonSummary(BaseModel):
    model_config = ConfigDict(frozen=True)
    workout_id: UUID
    average_effort_score: Optional[float] = None
    end_time: int
    leaderboard_rank: Optional[float] = None
    metrics_type: str
    name: str
    start_time: int
    timezone: Optional[str] = None
    total_leaderboard_users: Optional[int] = None
    total_work: float
    user_id: UUID
    workout_type: str
    ride: PelotonRideColumn

    @field_serializer('workout_id', 'user_id', when_used='always')
    def convert_uuid(uuid: UUID) -> str:
        return str(uuid)

    @field_validator('start_time', 'end_time')
    @classmethod
    def convert_timestamp(cls, ts: int) -> datetime:
        return datetime.fromtimestamp(ts, tz=EASTERN_TIME)

class PelotonWorkoutData(BaseModel):
    model_config = ConfigDict(frozen=True, coerce_numbers_to_str=True)
    workout_id: UUID
    summary_raw: dict = Field(repr=False)
    metrics_raw: dict = Field(repr=False)
    summary: PelotonSummary
    metrics: PelotonMetrics
    created_at: datetime = datetime.now(tz=EASTERN_TIME)

    @field_serializer('workout_id', when_used='always')
    def convert_uuid(uuid: UUID) -> str:
        return str(uuid)

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
    

            


def main():
    pprint(test_import()[0].model_dump())

if __name__ == '__main__':
    main()