import random
from pylotoncycle import pylotoncycle
from utils.constants import EASTERN_TIME, PELOTON_USERNAME, PELOTON_PASSWORD
import pandas as pd

list = []
for x in range(60):
    list.append(random.randint(1,20))

print(list)

for x in range(5):
    d1 = {random.randint(50,100): x for x in list }
    print(f"Dictionary Length: {len(d1)} entries")
    print(d1)

    d1.update({random.randint(50,100): x for x in list })


    print(f"Dictionary Length: {len(d1)} entries")
    print(d1.items())
    # print(d2)




# py_conn = pylotoncycle.PylotonCycle(PELOTON_USERNAME, PELOTON_PASSWORD)

# workouts = py_conn.GetRecentWorkouts(1)

# df_workout = pd.json_normalize(workouts[0])

# d2 = { column: df_workout[column][0] for column in df_workout.columns if not df_workout[column].dropna().empty }

# d3 = { column: df_workout[column][0] for column in df_workout.columns }

# print(d2)

# print(d3)

