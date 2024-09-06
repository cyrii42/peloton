from typing import Optional
from zoneinfo import ZoneInfo
from uuid import UUID, uuid4
from datetime import datetime

from pydantic import BaseModel, ConfigDict, AliasChoices, Field, field_validator, computed_field

LOCAL_TZ = ZoneInfo('America/New_York') 

class PelotonPivotTableRow(BaseModel):
    model_config = ConfigDict(frozen=True)
    id: UUID = Field(default_factory=uuid4, repr=False)
    month: Optional[str] = Field(alias=AliasChoices('Month'), default=None)
    year: Optional[int] = Field(alias=AliasChoices('Year'), default=None)
    rides: Optional[int] = Field(alias=AliasChoices('Rides'), default=None)
    days: Optional[int] = Field(alias=AliasChoices('Days'), default=None)
    total_hours: Optional[float] = Field(alias=AliasChoices('Hours'), default=None)
    total_miles: Optional[float] = Field(alias=AliasChoices('Miles'), default=None)
    avg_calories: Optional[float] = Field(alias=AliasChoices('Avg. Cals'), default=None)
    avg_output_min: Optional[float] = Field(alias=AliasChoices('OT/min'), default=None)
    
    @field_validator('total_hours', 'total_miles', 'avg_calories', 'avg_output_min')
    @classmethod
    def round_floats_to_two_decimal_places(cls, num: float | None) -> float | None:
        return None if num is None else round(num, 2)
        
    
class PelotonDataFrameRow(BaseModel):
    model_config = ConfigDict(frozen=True)
    workout_id: str = Field(repr=False)
    start_time: int | datetime | str = Field(repr=False)
    title: str
    instructor_name: Optional[str] = None
    image_url: Optional[str] = None
    leaderboard_rank: Optional[float] = None
    leaderboard_percentile: Optional[float] = None
    total_leaderboard_users: Optional[int] = None
    total_output: Optional[int] = None
    output_per_min: Optional[float] = None
    distance: Optional[float] = None
    calories: Optional[int] = None
    effort_score: Optional[float] = None
    
    @field_validator('leaderboard_rank', 'leaderboard_percentile', 'output_per_min', 'distance', 'effort_score')
    @classmethod
    def round_floats_to_two_decimal_places(cls, num: float | None) -> float | None:
        return None if num is None else round(num, 2)
    
    @field_validator('start_time')
    @classmethod
    def convert_timestamp(cls, dt: int | str | datetime) -> datetime:
        if isinstance(dt, int):
            return datetime.fromtimestamp(dt, tz=LOCAL_TZ)
        elif isinstance(dt, str):
            return datetime.fromisoformat(dt).astimezone(tz=LOCAL_TZ)
        elif isinstance(dt, datetime):
            return dt.astimezone(LOCAL_TZ)
        
    @computed_field
    def date(self) -> str:
        return self.start_time.strftime('%a, %h %-d, %Y') 
    
    @computed_field
    def time(self) -> str:
        return self.start_time.strftime('%-I:%M %p') 