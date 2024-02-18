from datetime import datetime, timedelta
from typing import Union
from uuid import UUID
from zoneinfo import ZoneInfo
from typing_extensions import Annotated, Optional, List

import sqlalchemy as db
from pydantic import BaseModel, ConfigDict, Field
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
    zones: Optional[List[PelotonMetricsEffortZoneSummary]] = None#Annotated[list[dict], Field(default_factory=lambda x: PelotonMetricsEffortZoneSummary.model_validate(x))]

class PelotonMetricsTotals(BaseModel):
    model_config = ConfigDict(frozen=True)
    display_name: str
    display_unit: str
    slug: str
    value: Optional[Union[int, float]] = None

class PelotonRideColumn(BaseModel):
    model_config = ConfigDict(frozen=True)
    description: str = Field(alias='ride_description')
    difficulty_estimate: float = Field(alias='ride_difficulty_estimate')
    duration: int = Field(alias='ride_duration')
    fitness_discipline: str = Field(alias='ride_fitness_discipline')
    id: UUID = Field(alias='ride_id')
    image_url: str = Field(alias='ride_image_url')
    instructor_id: str = Field(alias='ride_instructor_id')
    length: int = Field(alias='ride_length')
    title: str = Field(alias='ride_title')

class PelotonMetrics(BaseModel):
    model_config = ConfigDict(frozen=True)
    workout_id: UUID
    metrics: List[PelotonMetricsUnitSummary]#Annotated[list[dict], Field(default_factory=lambda x: PelotonMetricsUnitSummary.model_validate(x))]
    summaries: List[PelotonMetricsTotals]#Annotated[list[dict], Field(default_factory=lambda x: PelotonMetricsTotals.model_validate(x))]

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
    ride: Annotated[dict, Field(default_factory=lambda x: PelotonRideColumn.model_validate(x))]






def main():
    asdf = PelotonWorkoutID(workout_id='f2b4e32f10824ac3844df0ce41b06bfe')
    print(asdf)

if __name__ == '__main__':
    main()