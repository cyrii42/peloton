from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_serializer, field_validator
from typing_extensions import Optional

from .ride import PelotonRideColumn
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
    def convert_timestamp(cls, ts: int | str) -> datetime:
        if isinstance(ts, int):
            return datetime.fromtimestamp(ts, tz=EASTERN_TIME)
        elif isinstance(ts, str):
            return datetime.fromisoformat(ts).astimezone(tz=EASTERN_TIME)

    @field_serializer('start_time', 'end_time', when_used='always')
    def convert_datetime_to_string(dt: datetime) -> str:
        return dt.isoformat(sep='T', timespec='seconds')