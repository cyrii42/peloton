import pandas as pd
from pydantic import (BaseModel, ConfigDict, Field, computed_field,
                      field_validator)

from .metrics import PelotonMetrics
from .summary import PelotonSummary


class PelotonWorkoutData(BaseModel):
    model_config = ConfigDict(frozen=True)
    workout_id: str
    summary_raw: dict = Field(repr=False)
    metrics_raw: dict = Field(repr=False)
    summary: PelotonSummary
    metrics: PelotonMetrics

    @field_validator('workout_id')
    @classmethod
    def workout_id_is_UUID_not_all_zeroes(cls, workout_id: str) -> str:
        if workout_id is None or len(workout_id) != 32 or workout_id.count('0') == 32:
            raise ValueError("invalid Workout ID")
        else:
            return workout_id

    @computed_field
    def output_per_min(self) -> float | None:
        if (self.metrics.summaries is None 
                or self.summary.ride.ride_duration is None
                or self.summary.ride.ride_duration == 0):
            return None

        total_output = None
        for unit in self.metrics.summaries:
            if unit.slug == 'total_output':
                total_output = unit.value
        if total_output is None:
            return None

        ride_minutes = (self.summary.ride.ride_duration / 60)

        return (total_output / ride_minutes)

    @computed_field
    def duration_hrs(self) -> float | None:
        if self.summary.ride.ride_duration is None or self.summary.ride.ride_duration == 0:
            return None

        return (self.summary.ride.ride_duration / 3600)

    def create_dictionary(self) -> dict:
        # print(f"Making dataframe for workout {self.workout_id} at {datetime.now(tz=EASTERN_TIME)}...")
        output_dict = {}
        
        summary_dict = self.summary.model_dump(exclude={'ride'})
        output_dict.update(summary_dict)
        
        ride_dict = self.summary.ride.model_dump()
        output_dict.update(ride_dict)

        metrics_summaries_model_dump_list = [x.model_dump() for x in self.metrics.summaries]
        metrics_summaries_dict_list = [{d['slug']: d['value']} for d in metrics_summaries_model_dump_list]
        combined_dict = {key: value for d in metrics_summaries_dict_list for key, value in d.items()}
        output_dict.update(combined_dict)

        metrics_metrics_model_dump_list = [x.model_dump() for x in self.metrics.metrics]
        metrics_metrics_dict_list = ([{f"avg_{d['slug']}": d['average_value']} for d in metrics_metrics_model_dump_list] 
                                       + [{f"max_{d['slug']}": d['max_value']} for d in metrics_metrics_model_dump_list])
        combined_dict = {key: value for d in metrics_metrics_dict_list for key, value in d.items()}
        output_dict.update(combined_dict)

        metrics_hr_zones_model_dump_list = [x.model_dump() for x in self.metrics.metrics]
        metrics_hr_zones_dict_list = [d['zones'] for d in metrics_hr_zones_model_dump_list if d['zones'] is not None]
        if len(metrics_hr_zones_dict_list) > 0:
            metrics_hr_zones_dict_list = [{f"hr_{d['slug']}": d['duration']} for d in metrics_hr_zones_dict_list[0]]
            combined_dict = {key: value for d in metrics_hr_zones_dict_list for key, value in d.items()}
            output_dict.update(combined_dict)
  
        if self.metrics.effort_zones is not None:
            metrics_effort_zones_dict = self.metrics.effort_zones.model_dump()
            output_dict.update(metrics_effort_zones_dict)

        output_dict.update({'output_per_min': self.output_per_min, 'duration_hrs': self.duration_hrs})

        return output_dict

    def create_dataframe(self) -> pd.DataFrame:
        combined_dict = self.create_dictionary()
        return pd.DataFrame([combined_dict]).dropna(axis='columns', how='all')


def main():
    ...

if __name__ == '__main__':
    main()