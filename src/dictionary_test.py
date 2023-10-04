import random
from pylotoncycle import pylotoncycle
from utils.constants import EASTERN_TIME, PELOTON_USERNAME, PELOTON_PASSWORD
import pandas as pd
from dataclasses import dataclass
import inspect

list = []
for x in range(60):
    list.append(random.randint(1,20))

print(list)

@dataclass
class TestDataclass:
    id: int
    cheese: int
    barley: int
    
    @classmethod  # see https://stackoverflow.com/questions/54678337/how-does-one-ignore-extra-arguments-passed-to-a-dataclass
    def from_dict(cls, dict):    # "cls" is like "self" but for a @classmethod
        dataclass_fields = inspect.signature(cls).parameters  # an OrderedDict of the class attr keys
        return cls(**{  ## return a instantation of the class with the dict keypairs as parameters
            k: v for k, v in dict.items()   # items() returns the dict in a list of tuples
            if k in dataclass_fields  # checks if key is one of the class's parameters
        })

d1 = {'id': random.randint(50,100), 'cheese': random.randint(50,100), 'barley': random.randint(50,100) }
d1_testdataclass = TestDataclass.from_dict(d1)

print(d1_testdataclass)

# d1.update({random.randint(50,100): x for x in list })


# print(f"Dictionary Length: {len(d1)} entries")
# print(d1.items())
# # print(d2)

# print(make_request(d1))




# py_conn = pylotoncycle.PylotonCycle(PELOTON_USERNAME, PELOTON_PASSWORD)

# workouts = py_conn.GetRecentWorkouts(1)

# df_workout = pd.json_normalize(workouts[0])

# d2 = { column: df_workout[column][0] for column in df_workout.columns if not df_workout[column].dropna().empty }

# d3 = { column: df_workout[column][0] for column in df_workout.columns }

# print(d2)

# print(d3)

