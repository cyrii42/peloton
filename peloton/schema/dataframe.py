import datetime as dt
from typing import Optional
from decimal import Decimal
from pydantic import BaseModel, Field, field_validator

class PelotonDataFrameRow(BaseModel):
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
    output_per_min: Optional[Decimal] = Field(default=None)
    distance: Optional[Decimal] = Field(default=None)
    calories: Optional[int] = Field(default=None)
    effort_score: Optional[Decimal] = Field(default=None)

    @field_validator('leaderboard_rank', 'leaderboard_percentile', 
                     'output_per_min', 'distance', 'effort_score')
    @classmethod
    def quantize_decimal_fields(cls, num: Decimal | int | float | None) -> Decimal:
        if num is None:
            return None
        if isinstance(num, Decimal):
            return num.quantize(Decimal('1.00'))
        else:
            num = Decimal(num)
            return num.quantize(Decimal('1.00'))