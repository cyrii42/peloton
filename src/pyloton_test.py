import pandas as pd
from pylotoncycle import pylotoncycle
from utils.constants import EASTERN_TIME, PELOTON_USERNAME, PELOTON_PASSWORD

py_conn = pylotoncycle.PylotonCycle(PELOTON_USERNAME, PELOTON_PASSWORD)
workouts = py_conn.GetWorkoutMetricsById("1549b39e75cb48c0ac6179b952ce2cac")
df = pd.json_normalize(workouts)
df.to_csv('/mnt/home-ds920/metrics-10am.csv')

