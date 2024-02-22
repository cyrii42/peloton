from pydantic import BaseModel, ConfigDict, field_validator, Field
from typing_extensions import List, Optional


class PelotonMetricsEffortZoneSummary (BaseModel):
    model_config = ConfigDict(frozen=True)
    display_name: str
    duration: int
    max_value: int | float
    min_value: int | float
    range: str
    slug: str


class PelotonMetricsUnitSummary(BaseModel):
    model_config = ConfigDict(frozen=True)
    average_value: Optional[int | float] = Field(default=None)
    display_name: str
    display_unit: str
    max_value: Optional[int | float] = Field(default=None)
    slug: str
    values: Optional[List[int | float]] = None
    zones: Optional[List[PelotonMetricsEffortZoneSummary]] = None


class PelotonMetricsTotals(BaseModel):
    model_config = ConfigDict(frozen=True)
    display_name: str
    display_unit: str
    slug: str
    value: Optional[int | float] = Field(default=None)


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


