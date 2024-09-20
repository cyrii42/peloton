from sqlmodel import SQLModel, Field
from typing import Optional
import datetime as dt
from decimal import Decimal

from sqlmodel import JSON

from peloton.schema import PelotonAchievement, PelotonDataFrameRow

class DataframeBase(SQLModel):
    workout_id: str = Field(repr=False)
    start_time: dt.datetime = Field(repr=False)
    title: str
    # achievements: JSON
    instructor_name: Optional[str] = Field(default=None)
    image_url: Optional[str] = Field(default=None)
    leaderboard_rank: Optional[float] = Field(default=None)
    leaderboard_percentile: Optional[float] = Field(default=None)
    total_leaderboard_users: Optional[int] = Field(default=None)
    total_output: Optional[int] = Field(default=None)
    output_per_min: Optional[float] = Field(default=None)
    distance: Optional[float] = Field(default=None)
    calories: Optional[int] = Field(default=None)
    effort_score: Optional[float] = Field(default=None)

class DataframeCreate(DataframeBase):
    ...

class Dataframe(DataframeBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

def main():
    ...

if __name__ == '__main__':
    main()



# class DataframeBase(SQLModel):
#     workout_id: str
#     start_time: dt.datetime
#     end_time: dt.datetime
#     metrics_type: str
#     workout_type: str
#     leaderboard_rank: int
#     total_leaderboard_users: int
#     average_effort_score: float
#     achievements: PelotonAchievement
#     leaderboard_percentile: float
#     title: str
#     description: str
#     ride_length: int
#     ride_duration: int
#     image_url: str
#     difficulty_estimate: float
#     fitness_discipline: str
#     ride_id: str
#     total_output: int
#     distance: int
#     calories: int
#     avg_output: int
#     avg_cadence: int
#     avg_resistance: int
#     avg_speed: float
#     avg_heart_rate: int
#     max_output: int
#     max_cadence: int
#     max_resistance: int
#     max_speed: float
#     max_heart_rate: int
#     hr_zone1: int
#     hr_zone2: int
#     hr_zone3: int
#     hr_zone4: int
#     hr_zone5: int
#     effort_score: float
#     output_per_min: float
#     duration_hrs: float