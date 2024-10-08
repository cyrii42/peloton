from typing import Optional
from zoneinfo import ZoneInfo
from uuid import UUID, uuid4
from datetime import datetime
from pathlib import Path
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, AliasChoices, Field, field_validator, computed_field

LOCAL_TZ = ZoneInfo('America/New_York') 

class PelotonPivotTableRow(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)
    id: UUID = Field(default_factory=uuid4, repr=False)
    month: Optional[str] = Field(alias='Month', default=None)
    year: Optional[int] = Field(alias='Year', default=None)
    rides: Optional[int] = Field(alias='Rides', default=None)
    days: Optional[int] = Field(alias='Days', default=None)
    total_hours: Decimal = Field(alias='Hours')
    total_miles: Decimal = Field(alias='Miles')
    avg_calories: Decimal = Field(alias='Avg. Cals')
    avg_output_min: Decimal = Field(alias=AliasChoices('OT/min', 'avg_output/min'))

    @field_validator('total_hours', 'total_miles', 'avg_calories', 'avg_output_min')
    @classmethod
    def quantize_decimal_fields(cls, num: Decimal | int | float) -> Decimal:
        if isinstance(num, Decimal):
            return num.quantize(Decimal('1.00'))
        else:
            num = Decimal(num)
            return num.quantize(Decimal('1.00'))
        
    
class PelotonDataFrameRow(BaseModel):
    model_config = ConfigDict(frozen=True)
    workout_id: str = Field(repr=False)
    start_time: int | datetime | str = Field(repr=False)
    title: str
    instructor_name: Optional[str] = None
    image_url: Optional[str] = None
    leaderboard_rank: Optional[int] = None
    leaderboard_percentile: Optional[Decimal] = None
    total_leaderboard_users: Optional[int] = None
    total_output: Optional[int] = None
    output_per_min: Optional[Decimal] = None
    distance: Optional[Decimal] = None
    calories: Optional[int] = None
    effort_score: Optional[Decimal] = None
    
    @field_validator('leaderboard_percentile', 'output_per_min', 'distance')
    @classmethod
    def quantize_decimal_fields(cls, num: Decimal | int | float | None) -> Decimal:
        if num is None:
            return None
        if isinstance(num, Decimal):
            return num.quantize(Decimal('1.00'))
        else:
            num = Decimal(num)
            return num.quantize(Decimal('1.00'))

    @field_validator('effort_score')
    @classmethod
    def quantize_effort_score(cls, num: Decimal | int | float | None) -> Decimal:
        if num is None:
            return None
        if isinstance(num, Decimal):
            return num.quantize(Decimal('1.0'))
        else:
            num = Decimal(num)
            return num.quantize(Decimal('1.0'))
    
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

    @computed_field
    def image_url_html(self) -> str | None:
        if self.image_url is None:
            return None

        return f"<img class=\"table-pic\" src={self.image_url}></img>"

    @computed_field
    def image_url_html_local(self) -> str | None:
        if self.image_url is None:
            return None

        filename = self.image_url.split(sep='/')[-1]
        local_url = f"/workout_images/{filename}"
        return f"<img class=\"table-pic\" src={local_url}></img>"

    @computed_field
    def image_url_html_local_thumb(self) -> str | None:
        if self.image_url is None:
            return None

        filename = self.image_url.split(sep='/')[-1]
        filepath = Path(filename)
        thumb_filename = f"{filepath.stem}_thumb{filepath.suffix}"
        
        thumb_url = f"/workout_images/{thumb_filename}"
        return f"<img class=\"table-pic\" src={thumb_url}></img>"