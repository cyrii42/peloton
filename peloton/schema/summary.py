from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_serializer, field_validator, computed_field, Field, AliasChoices
from typing import Optional

from .ride import PelotonRideColumn
from .achievement import PelotonAchievement
from peloton.constants import EASTERN_TIME

     

class PelotonSummary(BaseModel):
    model_config = ConfigDict(frozen=True)
    workout_id: str
    start_time: int | datetime | str
    end_time: int | datetime | str
    metrics_type: str
    workout_type: str
    leaderboard_rank: Optional[int] = None
    total_leaderboard_users: Optional[int] = None
    average_effort_score: Optional[float] = None
    achievements: Optional[list[PelotonAchievement]] = Field(alias=AliasChoices('achievement_templates', 'achievements'), default=None)
    ride: PelotonRideColumn

    @computed_field
    def leaderboard_percentile(self) -> float:
        if self.total_leaderboard_users is None or self.leaderboard_rank is None:
            return None
        else:
            return ((self.total_leaderboard_users - self.leaderboard_rank) / self.total_leaderboard_users)*100
    
    @field_validator('workout_id')
    @classmethod
    def workout_id_is_UUID_not_all_zeroes(cls, workout_id: str) -> str:
        if workout_id is None or len(workout_id) != 32 or workout_id.count('0') == 32:
            raise ValueError("invalid Workout ID")
        else:
            return workout_id

    @field_validator('start_time', 'end_time')
    @classmethod
    def convert_timestamp(cls, dt: int | str | datetime) -> datetime:
        if isinstance(dt, int):
            return datetime.fromtimestamp(dt, tz=EASTERN_TIME)
        elif isinstance(dt, str):
            return datetime.fromisoformat(dt).astimezone(tz=EASTERN_TIME)
        elif isinstance(dt, datetime):
            return dt.astimezone(EASTERN_TIME)

    @field_serializer('start_time', 'end_time', when_used='always')
    def convert_datetime_to_string(dt: datetime) -> str:
        if isinstance(dt, datetime):
            return dt.isoformat(sep='T', timespec='seconds')
        elif isinstance(dt, str):
            return dt