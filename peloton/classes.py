import inspect
from dataclasses import dataclass
from datetime import datetime
from typing import List
from zoneinfo import ZoneInfo

import pandas as pd

from peloton.constants import EASTERN_TIME


@dataclass
class PelotonRide:
    workout_id: str = None
    start_time: int = None
    start_time_iso: str = None
    end_time: int = None
    end_time_iso: str = None
    ride_title: str = None
    instructor_name: str = None
    ride_instructor_id: str = None
    ride_description: str = None
    user_id: str = None
    ride_id: str = None
    ride_image_url: str = None
    timezone: str = None
    metrics_type: str = None
    total_work: float = None
    has_pedaling_metrics: str = None
    has_leaderboard_metrics: str = None
    workout_type: str = None
    average_effort_score: float = None
    leaderboard_rank: int = None
    total_leaderboard_users: int = None
    ride_duration: int = None
    ride_length: int = None
    distance: float = None
    ride_difficulty_estimate: float = None
    calories: float = None
    total_output: float = None
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
    
    # adapted from:
    # https://stackoverflow.com/questions/54678337/how-does-one-ignore-extra-arguments-passed-to-a-dataclass
    @classmethod
    def from_dict(cls, dict):    # "cls" is like "self" but for a @classmethod
        dataclass_fields = inspect.signature(cls).parameters  # an OrderedDict of the class attr keys
        return cls(**{  ## return a instantation of the class with the dict keypairs as parameters
            k: v for k, v in dict.items()   # items() returns the dict in a list of tuples
            if k in dataclass_fields  # checks if key is one of the class's parameters
        })
    
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