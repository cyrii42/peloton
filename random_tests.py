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

import math
from collections import OrderedDict
from datetime import date, datetime, timedelta
from pprint import pprint
from typing import Annotated, Optional, Union
from uuid import UUID, uuid4

import pandas as pd
from pydantic import BaseModel, BeforeValidator, ConfigDict, Field, computed_field, field_validator, model_validator
from zoneinfo import ZoneInfo

from peloton import PelotonProcessor, PelotonWorkoutData, PelotonImageDownloader
from peloton.constants import EASTERN_TIME

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
    instructor_name: Optional[str] = None
    image_url: Optional[str] = None
    leaderboard_rank: Optional[float] = None
    leaderboard_percentile: Optional[float] = None
    total_leaderboard_users: Optional[int] = None
    total_output: Optional[int] = None
    output_per_min: Optional[float] = None
    distance: Optional[float] = None
    calories: Optional[int] = None
    effort_score: Optional[float] = None
    
    @field_validator('leaderboard_rank', 'leaderboard_percentile', 'output_per_min', 'distance', 'effort_score')
    @classmethod
    def round_floats_to_two_decimal_places(cls, num: float | None) -> float | None:
        return None if num is None else round(num, 2)
    
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

desired_columns = ['date', 'time', 'title', 'instructor_name', 'total_output', 'output_per_min', 
                        'distance', 'calories', 'effort_score', 'start_time']

list_of_dicts = peloton.make_list_of_dicts()
rows = [PelotonDataFrameRow.model_validate(row).model_dump(include=desired_columns)
            for row in list_of_dicts]
# print(rows)

# for row in rows:
#     print(datetime.strptime(date_string=f"{row.get('date')} {row.get('time')}", format='%a, %b %d, %Y %H:%M %p'))

# reordered_rows = [{key: row.get(key) for key in desired_columns} for row in rows]
# print(reordered_rows)
    
# sorted_rows = sorted(reordered_rows, key=lambda row: datetime.strptime(f"{row.get('date')} {row.get('time')}", format='%a, %b %d, %Y %H:%M %p'), reverse=True)
# for row in sorted_rows:
#     print(row.get('date'))
    
#row.get('start_time')

from PIL import Image
from pathlib import Path

def create_thumbnail(img: Image) -> Image:
    return img.thumbnail()

img_path = Path.cwd().joinpath('data', 'workout_images', 'img_1721845105_e293119d5f384556ad710cc87756a034.jpg')

# img = Image.open(img_path)

# thumb = img.copy()

# thumb.thumbnail(size=(120, 120))

# thumb.save('test.jpg')

# def create_thumbnail_filename(filename: Path) -> Path:
#     filename.stem = f"{filename.stem}_thumb"
#     return filename

# thumb_filename = img_path.with_stem(f"{img_path.stem}_thumb")

# print(thumb_filename)

# with open('test.jpg', 'rb') as f:
#     f.write(thumb)


# test_workout = peloton.workouts[150]
# peloton.image_downloader.download_workout_image(test_workout)

img_path_str = str(img_path.name)

def convert_str_filename(filename: str) -> str:
    filepath = Path(filename)
    print(f"{filepath.stem}_thumb{filepath.suffix}")
    # file_ext = filename.split('.')[-1]
    # print(file_ext)

    # file_stem = (filename.split('/')[-1]).split('.')[0]
    # thumb_filename = f"{file_stem}_thumb.{file_ext}"

    # print(thumb_filename)
print(img_path_str)
convert_str_filename(img_path_str)