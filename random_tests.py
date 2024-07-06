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
from peloton.constants import EASTERN_TIME
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