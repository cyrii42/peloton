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

print(634 / 60)