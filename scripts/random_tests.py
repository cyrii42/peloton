# from pathlib import Path


# # WORKOUTS_DIR = Path.home().joinpath('python', 'peloton', 'data', 'workouts')

# # print(f"sqlite:///{Path.home().joinpath('python', 'peloton', 'data', 'peloton.db').resolve()}")
# # print([type(file) for file in WORKOUTS_DIR.iterdir()])

# workouts_on_disk = ['a', 'b', 'c', 'd', 'e']
# workouts_on_peloton = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j']

# new_workouts_num = len(workouts_on_peloton) - len(workouts_on_disk)
# print(f"New workouts on peloton: {new_workouts_num}")

# new_workouts = workouts_on_peloton[-abs(new_workouts_num):]
# print(new_workouts)

# print(f"Workout IDs do not match: {workouts_on_disk}",
#                            f"vs. {workouts_on_peloton}")

# import pandas as pd

# workout_list = []

# print(pd.concat([workout.create_dataframe() for workout in workout_list], ignore_index=True)
#                   .sort_values(by=['start_time'])
#                   .reset_index(drop=True))


# d1 = dict()
# d1.update({'fart': 3, 'boop': 44})
# print(list(**d1))

from datetime import timedelta, date, datetime
from peloton import EASTERN_TIME
import pandas as pd
from uuid import UUID, uuid4
from typing import Optional, Annotated, Union
from pprint import pprint
from zoneinfo import ZoneInfo
from collections import OrderedDict
import math

from peloton import PelotonProcessor, PelotonWorkoutData, WORKOUTS_DIR

from pydantic import BaseModel, ConfigDict, Field, field_validator, computed_field, model_validator,  BeforeValidator

LOCAL_TZ = ZoneInfo('America/New_York')

DAYS = 30
curr_start_date = date.today() - timedelta(days=(DAYS - 1))
curr_end_date = date.today()

prev_start_date = date.today() - timedelta(days=((DAYS * 2) - 1))
prev_end_date = date.today() - timedelta(days=DAYS)

print(f"Current start date: {curr_start_date}")
print(f"Current end date: {curr_end_date}")
print(f"Previous start date: {prev_start_date}")
print(f"Previous end date: {prev_end_date}")

DURATION = 26705
print(f"{DURATION // 3600} hours, {DURATION % 3600 // 60} minutes")

print(f"Today: {date.today().weekday()}")
print(f"Previous Monday: {date.today() - timedelta(days=(date.today().weekday()))}")
print([char for char in 'asoiasdfoihaspdfoihaspdofihaspofihapsoifhapsoidfhfhasoidfh'])
print(datetime.now(tz=EASTERN_TIME).date())
print(datetime.now().replace(hour=0, minute=0, second=0, microsecond=0))

asdf = int(round((datetime.now(tz=EASTERN_TIME).replace(hour=0, minute=0, second=0, microsecond=0) 
                             - timedelta(days=30)).timestamp()))

print(datetime.fromtimestamp(asdf, tz=EASTERN_TIME))

# class PelotonMonthTableRow(BaseModel):
#     model_config = ConfigDict(frozen=True)
#     id: UUID = Field(default_factory=uuid4, repr=False)
#     month: str
#     rides: float
#     days: float
#     total_hours: float
#     total_miles: float
#     avg_calories: float
#     avg_output_min: float

class PelotonTableRow(BaseModel):
    model_config = ConfigDict(frozen=True)
    id: UUID = Field(default_factory=uuid4, repr=False)
    month: Optional[str] = None
    year: Optional[int] = None
    rides: Optional[int] = None
    days: Optional[int] = None
    total_hours: float
    total_miles: float
    avg_calories: float
    avg_output_min: float

# df = pd.read_csv('./data/year_table.csv', index_col=0).rename(columns={'avg_output/min': 'avg_output_min'})

# row_list = [PelotonTableRow.model_validate(row) for row in df.to_dict('records')]

# for row in row_list:
#     print(row)
    
# pprint(PelotonTableRow.model_json_schema()['properties'].keys())

# test_row = row_list[0]
# columns = [x[0] for x in test_row.__repr_args__() if x[1] is not None]
# columns = row_list[0].model_fields
# print(columns)

def check_for_nans(v):
    if isinstance(v, float):
        if math.isnan(v):
            return None
        else:
            return round(v, 2)
    else:
        return v    

class PelotonDataFrameRow(BaseModel):
    model_config = ConfigDict(frozen=True)
    workout_id: str = Field(repr=False)
    start_time: int | datetime | str = Field(repr=False)
    title: str
    instructor_name: str = None
    image_url: str = None
    leaderboard_rank: int = None
    leaderboard_percentile: float = None
    total_leaderboard_users: int = None
    total_output: int = None
    output_per_min: float = None
    distance: float = None
    calories: int = None
    effort_score: float = None
    
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
    
# df = pd.read_csv('./data/processed_workouts_data.csv', index_col=0)
# # print(df.to_dict('records'))
# asdf = PelotonDataFrameRow.model_validate(df.to_dict('records')[149]).model_dump(exclude=['workout_id', 'start_time'])
# print(asdf)
# od = OrderedDict(asdf)
# print(od.keys())
# desired_order = ['date', 'time', 'title', 'instructor_name', 'leaderboard_rank',
#                  'leaderboard_percentile', 'total_leaderboard_users', 'total_output', 'output_per_min', 
#                  'distance', 'calories', 'effort_score']

# for col in desired_order:
#     od.move_to_end(col)
# print(od)

print()

peloton = PelotonProcessor()

dicts = peloton.make_list_of_dicts()
asdf2 = PelotonDataFrameRow.model_validate(dicts[149]).model_dump(exclude=['workout_id', 'start_time'])
print(asdf2)

def get_workouts_from_json() -> list[PelotonWorkoutData]:
    try:
        json_files = [file for file in WORKOUTS_DIR.iterdir() if file.suffix == '.json']
    except FileNotFoundError:
        return list()
    
    if len(json_files) == 0:
        print('noooope')
        return list()

    output_list = []
    for file in json_files:
        with open(file, 'r') as f:
            output_list.append(PelotonWorkoutData.model_validate_json(f.read()))
    return output_list

# print(WORKOUTS_DIR)
# print(get_workouts_from_json())
# print([file for file in WORKOUTS_DIR.iterdir() if file.suffix == '.json'])
# print('')
# print(peloton.get_workout_object_from_id('0c1c95a693d34c96a5d62f965794472f'))