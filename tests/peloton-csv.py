from pylotoncycle import pylotoncycle
from utils.config import peloton_username, peloton_password

# Create PylotonCycle connection object
py_conn = pylotoncycle.PylotonCycle(peloton_username, peloton_password)

# Get the total number of workouts from Peloton
total_workouts = py_conn.GetMe()["total_workouts"]

# Retrieve the new workout data from Peleton
workouts = py_conn.GetRecentWorkouts(total_workouts)

with open('/home/zvaughan/docker/workouts_aug28.txt', 'w') as f:
    f.write(str(workouts))