from datetime import datetime, timedelta
from typing import Union
from uuid import UUID
from zoneinfo import ZoneInfo
from typing_extensions import Optional, List

import sqlalchemy as db
from pydantic import BaseModel, ConfigDict, Field, computed_field, field_serializer
from sqlalchemy.orm import declarative_base

EASTERN_TIME = ZoneInfo('America/New_York')

class PelotonWorkoutID(BaseModel):
    model_config = ConfigDict(frozen=True, coerce_numbers_to_str=True)
    workout_id: UUID
    fart: Optional[str] = None
    created_at: datetime = datetime.now(tz=EASTERN_TIME)

class PelotonRawMetrics(BaseModel):
    model_config = ConfigDict(frozen=True)
    data: dict

class PelotonRawSummary(BaseModel):
    model_config = ConfigDict(frozen=True)
    data: dict

class PelotonInstructor(BaseModel):
    model_config = ConfigDict(frozen=True)
    instructor_id: str = Field(alias='id')
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

    # @field_serializer('instructor_id', when_used='json')
    # def serialize_courses_in_order(instructor_id: UUID):
    #     return str(instructor_id)

class PelotonInstructorDict(BaseModel):
    instructor_id: UUID
    instructor: PelotonInstructor
    

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

class PelotonRideColumn(BaseModel):
    model_config = ConfigDict(frozen=True)
    ride_description: str = Field(alias='description', default=None)
    ride_difficulty_estimate: float = Field(alias='difficulty_estimate', default=None)
    ride_duration: int = Field(alias='duration')
    ride_fitness_discipline: str = Field(alias='fitness_discipline', default=None)
    ride_id: UUID = Field(alias='id')
    ride_image_url: str = Field(alias='image_url', default=None)
    ride_instructor: Optional[str] = Field(alias='instructor', default=None)
    ride_instructor_id: Optional[str] = Field(alias='instructor_id', default=None)
    ride_length: int = Field(alias='length', default=None)
    ride_title: str = Field(alias='title')

class PelotonMetrics(BaseModel):
    model_config = ConfigDict(frozen=True)
    workout_id: UUID
    metrics: List[PelotonMetricsUnitSummary]
    summaries: List[PelotonMetricsTotals]

class PelotonSummary(BaseModel):
    model_config = ConfigDict(frozen=True)
    workout_id: UUID
    average_effort_score: Optional[float] = None
    end_time: int  # create datetime?
    leaderboard_rank: Optional[float] = None
    metrics_type: str
    name: str
    start_time: int # create datetime?
    timezone: Optional[str] = None
    total_leaderboard_users: Optional[int] = None
    total_work: float
    user_id: UUID
    workout_type: str
    ride: PelotonRideColumn





def main():
    asdf = PelotonWorkoutID(workout_id='f2b4e32f10824ac3844df0ce41b06bfe')
    print(asdf)

if __name__ == '__main__':
    main()