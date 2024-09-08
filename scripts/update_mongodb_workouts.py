from peloton import PelotonProcessor
import pandas as pd
from pprint import pprint

peloton = PelotonProcessor()

# peloton.reprocess_mongodb_data()

achievements_list = [workout.summary.achievements for workout in peloton.workouts if workout.summary.achievements is not None]
achievements = [item.model_dump() for row in achievements_list for item in row]
pprint(achievements)

df = pd.DataFrame([item for item in achievements])
print(df)