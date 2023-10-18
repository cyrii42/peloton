import inspect
from dataclasses import dataclass, field
from datetime import datetime
from typing import List
from zoneinfo import ZoneInfo

import pandas as pd
from typing_extensions import Self

from peloton.constants import EASTERN_TIME


@dataclass
class PelotonRide:
    workout_id: str
    timezone: str
    start_time: int
    start_time_iso: str = field(init=False)
    end_time: int
    end_time_iso: str = field(init=False)
    ride_title: str
    workout_type: str
    metrics_type: str
    user_id: str
    distance: float
    calories: float
    total_output: float
    instructor_name: str
    total_work: float = None
    ride_instructor_id: str = None
    ride_description: str = None
    ride_difficulty_estimate: float = None
    ride_id: str = None
    ride_image_url: str = None
    has_pedaling_metrics: str = None
    has_leaderboard_metrics: str = None
    average_effort_score: float = None
    leaderboard_rank: int = None
    total_leaderboard_users: int = None
    ride_duration: int = None
    ride_length: int = None
    output_avg: int = None
    output_max: int = None
    cadence_avg: int = None
    cadence_max: int = None
    resistance_avg: int = None
    resistance_max: int = None
    speed_avg: float = None
    speed_max: float = None
    heart_rate_avg: int = None
    heart_rate_max: int = None
    strive_score: float = None
    heart_rate_z1_duration: int = None
    heart_rate_z2_duration: int = None
    heart_rate_z3_duration: int = None
    heart_rate_z4_duration: int = None
    heart_rate_z5_duration: int = None
    
    @classmethod
    def from_dict(cls, dict) -> Self:
        """ Instantiates a new object of this dataclass with attributes populated from a (potentially overinclusive) dictionary.  

            * ``inspect.signature(cls).parameters`` returns an OrderedDict containing this dataclass's attribute keys.
            * ``{ k: v for k, v in dict.items() if k in dataclass_fields })`` is a dictionary comprehension that collects
            key/value pairs for all dict entries that correspond with one of the dataclass's attribute keys.
            * ``cls(**)`` then unpacks the key/value pairs and instantiates a new object of class "cls" (i.e., this class) 
            with those key/value pairs as its attributes.

        (Adapted from https://stackoverflow.com/questions/54678337/how-does-one-ignore-extra-arguments-passed-to-a-dataclass)
        """
        dataclass_fields = inspect.signature(cls).parameters
        return cls(**{ k: v for k, v in dict.items() if k in dataclass_fields })
    
    def __post_init__(self):
        if self.start_time:          
            if self.timezone:
                self.start_time_iso = datetime.fromtimestamp(self.start_time, tz=ZoneInfo(self.timezone)).isoformat()
            else:
                self.start_time_iso = datetime.fromtimestamp(
                    self.start_time, tz=EASTERN_TIME).isoformat()
        if self.end_time:          
            if self.timezone:
                self.end_time_iso = datetime.fromtimestamp(self.end_time, tz=ZoneInfo(self.timezone)).isoformat()
            else:
                self.end_time_iso = datetime.fromtimestamp(
                    self.end_time, tz=EASTERN_TIME).isoformat()   
                
    # Added "dropna(axis='columns')" to drop empty columns and avoid FUTUREWARNING: 
    #       "FutureWarning: The behavior of DataFrame concatenation with empty 
    #       or all-NA entries is deprecated. In a future version, this will no longer
    #       exclude empty or all-NA columns when determining the result dtypes. To retain 
    #       the old behavior, exclude the relevant entries before the concat operation."
    def create_dataframe(self):
        return pd.DataFrame([self]).dropna(axis='columns', how='all')   #.set_index('id')
    
    
    
@dataclass
class PelotonRideGroup:
    rides: List[PelotonRide]
    
    def __str__(self):
        string = ""
        for ride in self.rides:
            string = string + "\n" + "\n" + ride.__repr__()
        return f"{self.__class__.__name__} ({len(self.rides)} rides):{string}"
    
    def create_dataframe(self):
        rides_list = [ride.create_dataframe() for ride in reversed(self.rides)]
        
        return pd.concat(rides_list, ignore_index=True)  # if set_index('id') above, set ignore_index=False 