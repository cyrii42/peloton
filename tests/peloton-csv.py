from pylotoncycle import pylotoncycle
from peloton.constants import PELOTON_USERNAME, PELOTON_PASSWORD

# Create PylotonCycle connection object
py_conn = pylotoncycle.PylotonCycle(PELOTON_USERNAME, PELOTON_PASSWORD)

# Get the total number of workouts from Peloton
total_workouts = py_conn.GetMe()["total_workouts"]

# Retrieve the new workout data from Peleton
workouts = py_conn.GetRecentWorkouts(total_workouts)

with open('/home/zvaughan/docker/workouts_aug28.txt', 'w') as f:
    f.write(str(workouts))