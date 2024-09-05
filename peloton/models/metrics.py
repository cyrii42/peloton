from pydantic import BaseModel, ConfigDict, field_validator, Field, AliasChoices
from typing_extensions import Optional


class PelotonMetricsMetricsHeartRateZone (BaseModel):
    model_config = ConfigDict(frozen=True)
    display_name: str
    duration: int
    max_value: int | float
    min_value: int | float
    range: str
    slug: str


class PelotonMetricsMetrics(BaseModel):
    model_config = ConfigDict(frozen=True)
    average_value: Optional[int | float] = Field(default=None)
    display_name: str
    display_unit: str
    max_value: Optional[int | float] = Field(default=None)
    slug: str
    values: Optional[list[int | float]] = None
    zones: Optional[list[PelotonMetricsMetricsHeartRateZone]] = None


class PelotonMetricsSummaries(BaseModel):
    model_config = ConfigDict(frozen=True)
    display_name: str
    display_unit: str
    slug: str
    value: Optional[int | float] = Field(default=None)

class PelotonMetricsEffortZones(BaseModel):
    model_config = ConfigDict(frozen=True)
    effort_score: float = Field(alias=AliasChoices('total_effort_points', 'effort_score'))
    # heart_rate_zone_durations: dict

class PelotonMetricsSplitMetricsMetricsData(BaseModel):
    slug: str
    value: Optional[float] = None
    unit: str

class PelotonMetricsSplitMetricsHeader(BaseModel):
    slug: str
    display_name: str

class PelotonMetricsSplitMetricsMetrics(BaseModel):
    is_best: bool
    has_floor_segment: bool
    data: list[PelotonMetricsSplitMetricsMetricsData]
    
class PelotonMetricsSplitMetrics(BaseModel):
    header: Optional[list[PelotonMetricsSplitMetricsHeader]] = None
    metrics: Optional[list[PelotonMetricsSplitMetricsMetrics]] = None

class PelotonMetricsSplitsDataSplit(BaseModel):
    distance_marker: float
    order: int
    seconds: float
    elevation_change: Optional[float] = None
    has_floor_segment: bool
    is_best: bool

class PelotonMetricsSplitsData(BaseModel):
    distance_marker_display_unit: Optional[str] = None
    elevation_change_display_unit: Optional[str] = None
    splits: Optional[list[PelotonMetricsSplitsDataSplit]] = None

class PelotonMetrics(BaseModel):
    model_config = ConfigDict(frozen=True)
    workout_id: str
    metrics: list[PelotonMetricsMetrics]
    summaries: list[PelotonMetricsSummaries]
    effort_zones: Optional[PelotonMetricsEffortZones] = None
    splits_data: Optional[PelotonMetricsSplitsData] = None
    splits_metrics: Optional[PelotonMetricsSplitMetrics] = None


    @field_validator('workout_id')
    @classmethod
    def workout_id_is_UUID_not_all_zeroes(cls, workout_id: str) -> str:
        if workout_id is None or len(workout_id) != 32 or workout_id.count('0') == 32:
            raise ValueError("invalid Workout ID")
        else:
            return workout_id


