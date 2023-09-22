## List of functions
# GetMe(self)
# GetUrl(self,url)
# GetWorkoutList(self, num_workouts=None)
# GetRecentWorkouts(self, num_workouts=None)
# GetWorkoutSummaryById(self, workout_id)
# GetWorkoutMetricsById (self, workout_id, frequency=50)
# GetWorkoutById(self, workout_id)
# GetInstructorById(self, instructor_id)
# GetFollowersById(self, userid=None)

from datetime import datetime
import pandas as pd
from pylotoncycle import pylotoncycle
from src.config.config import peloton_username, peloton_password
from utils.time import eastern_time

# Create PylotonCycle connection object
py_conn = pylotoncycle.PylotonCycle(peloton_username, peloton_password)

# Calculate number of new workouts not yet in DB
def calculate_new_workouts_num(df_input: pd.DataFrame) -> int:
    total_workouts = py_conn.GetMe()["total_workouts"]
    existing_workouts = df_input.shape[0]
    new_workouts = total_workouts - existing_workouts

    print("Total Workouts: " + str(total_workouts))
    print("Workouts in Database: " + str(existing_workouts))
    print("New Workouts to Write: " + str(new_workouts))
    
    return new_workouts

# Retrieve new workouts (if any) from Peloton and create Pandas DataFrame from dict of lists
def get_new_workouts(new_workouts_num: int) -> pd.DataFrame:
    peloton_dict = {
    'start_time_iso': [],
    'start_time_local': [],
    'instructor': [],
    'title': [],
    'duration': [],
    'length': [],
    'output': [],
    'calories': [],
    'cadence_avg': [], 
    'cadence_max': [],
    'resistance_avg': [],
    'resistance_max': [],
    'speed_avg': [],
    'speed_max': [],
    'hr_avg': [], 
    'hr_max': [],
    'effort_points': [],
    'distance': [],
    'difficulty': []    
    }

    if new_workouts_num == 0:
        return pd.DataFrame(peloton_dict)
    
    else:
        workouts = py_conn.GetRecentWorkouts(new_workouts_num)
        
        for w in reversed(workouts):
            # Define necessary lists
            workout_id = w['id']
            ride = w["ride"]
            workout_metrics = py_conn.GetWorkoutMetricsById(workout_id)
            summaries = workout_metrics["summaries"]
            metrics = workout_metrics["metrics"]
            effort_zones = workout_metrics["effort_zones"]

            # Start Time ISO & Start Time Local
            start_timestamp = w["start_time"]
            start_time_iso = datetime.fromtimestamp(start_timestamp, tz=eastern_time).isoformat(sep='T')
            peloton_dict['start_time_iso'].append(start_time_iso)
            start_time_local = datetime.fromtimestamp(start_timestamp, tz=None)
            peloton_dict['start_time_local'].append(start_time_local)

            # Instructor
            # inst_id = conn.GetWorkoutSummaryById(workout_id)["ride"]["instructor_id"]
            # inst = conn.GetInstructorById(inst_id)["name"]
            # row.append(inst)
            #inst = w["instructor_name"]
            peloton_dict['instructor'].append(w.get("instructor_name", None))
            
            # Title
            #title = ride["title"]
            peloton_dict['title'].append(ride.get("title", None))

            # Duration
            #duration = ride["duration"]
            #### PREVIOUSLY:
            # if ride.get('duration') == None:
            #     peloton_dict['duration'].append(None)
            # else:
            #     peloton_dict['duration'].append(ride.get("duration", 0))
            if ride.get('duration') == None:
                if ride.get('length') == None:
                    peloton_dict['duration'].append(None)
                else:
                    peloton_dict['duration'].append(ride.get('length', 0))
            else:
                peloton_dict['duration'].append(ride.get('duration', 0))

            # Length
            #length = ride["length"]
            if ride.get('length') == None:
                if ride.get('duration') == None:
                    peloton_dict['length'].append(None)
                else:
                    peloton_dict['length'].append(ride.get('duration', 0))
            else:
                peloton_dict['length'].append(ride.get('length', 0))

            # Output
            #total_output = summaries[2]["value"]
            if len(summaries) >= 1:
                summary_output = summaries[0]
                peloton_dict['output'].append(summary_output.get("value", 0))
            else:
                peloton_dict['output'].append(None)
            
            # Calories
            #cals = summaries[2]["value"]
            if len(summaries) >= 3:
                summary_cals = summaries[2]
                peloton_dict['calories'].append(summary_cals.get("value", 0))
            else:
                peloton_dict['calories'].append(None)

            # Cadence (Avg) & Cadence (Max)
            #cadence_avg = metrics[1]["average_value"]
            #cadence_max = metrics[1]["max_value"]
            if len(metrics) >= 2:
                metrics_cadence = metrics[1]
                peloton_dict['cadence_avg'].append(metrics_cadence.get("average_value", 0))
                peloton_dict['cadence_max'].append(metrics_cadence.get("max_value", 0))
            else:
                peloton_dict['cadence_avg'].append(None)
                peloton_dict['cadence_max'].append(None)

            # Resistance (Avg) & Resistance (Max)
            #resistance_avg = metrics[2]["average_value"]   
            #resistance_max = metrics[2]["max_value"]
            if len(metrics) >= 3:
                metrics_resistance = metrics[2]
                peloton_dict['resistance_avg'].append(metrics_resistance.get("average_value", 0))
                peloton_dict['resistance_max'].append(metrics_resistance.get("max_value", 0))
            else:
                peloton_dict['resistance_avg'].append(None)
                peloton_dict['resistance_max'].append(None)

            # Speed (Avg) & Speed (Max)
            #speed_avg = metrics[3]["average_value"]
            #speed_max = metrics[3]["max_value"]
            if len(metrics) >= 4:
                metrics_speed = metrics[3]
                peloton_dict['speed_avg'].append(metrics_speed.get("average_value", ""))
                peloton_dict['speed_max'].append(metrics_speed.get("max_value", ""))
            else:
                peloton_dict['speed_avg'].append(None)
                peloton_dict['speed_max'].append(None)

            # Heart Rate (Avg) & Heart Rate (Max) & Effort Points
            #hr_avg = metrics[4]["average_value"]
            #hr_max = metrics[4]["max_value"]
            #total_effort_points = metrics["total_effort_points"]
            if len(metrics) >= 5:
                metrics_hr = metrics[4]
                peloton_dict['hr_avg'].append(metrics_hr.get("average_value", 0))
                peloton_dict['hr_max'].append(metrics_hr.get("max_value", 0))
                peloton_dict['effort_points'].append(workout_metrics.get("effort_zones", {}).get("total_effort_points"))
            else:
                peloton_dict['hr_avg'].append(None)
                peloton_dict['hr_max'].append(None)
                peloton_dict['effort_points'].append(None)

            # Distance
            #distance = summaries[1]["value"]
            if len(summaries) >= 2:
                summary_distance = summaries[1]
                peloton_dict['distance'].append(summary_distance.get("value", ""))
            else:
                peloton_dict['distance'].append(None)

            # Difficulty
            #difficulty = ride["difficulty_estimate"]
            if ride.get('difficulty_estimate') == None:
                peloton_dict['difficulty'].append(None)
            else:
                peloton_dict['difficulty'].append(ride.get('difficulty_estimate', 0))
                
        return pd.DataFrame(peloton_dict)