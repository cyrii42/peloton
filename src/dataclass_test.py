import pandas as pd
from peloton_to_mariadb import ingest_sql_data, calculate_new_workouts_num, export_to_sql, get_new_workouts
from utils.peloton_pivots import get_sql_data_for_pivots, get_pivot_table_year, get_pivot_table_month
from dataclasses import dataclass
import json
from pylotoncycle import pylotoncycle
from utils.constants import EASTERN_TIME, PELOTON_USERNAME, PELOTON_PASSWORD
from utils.helpers import create_mariadb_engine

# Create PylotonCycle connection object
py_conn = pylotoncycle.PylotonCycle(PELOTON_USERNAME, PELOTON_PASSWORD)

# GetWorkoutList(self, num_workouts=None)
# GetWorkoutSummaryById(self, workout_id)
# GetWorkoutById(self, workout_id)
# GetInstructorById(self, instructor_id)
# GetFollowersById(self, userid=None)


# @dataclass
# class PelotonRide:
#     name: str
    
# asdf = PelotonRide("bongo billy")

# print(asdf)


##### This might be a nice upgrade, but consider moving everything to a Dataclass.  Then you
##### might be able to specify default "None" values for some of these things, which means you could
##### dispense with all the checking.

# Check if specified column (or alternate column) exists in DataFrame; if so, return full column (as a Series)
def check_column(column: str, df: pd.DataFrame, alternate_column: str=None) -> pd.Series | None:
    if column in df.columns:
        return df[column]
    elif alternate_column in df.columns:
        return df[alternate_column]
    else:
        if alternate_column == None:
            print(f"Columnn {column} does not exist!")
        else:
            print(f"Neither column {column} nor column {alternate_column} exists!")
        return None
    
    
# Check if specified row number exists; if so, return the value of that row in specified column
def check_row(row: int, column: str, df: pd.DataFrame) -> pd.Series | None:
    if row < df.shape[0]:
        return df[column][row]
    else:
        print(f"Row #{row} does not exist!")
        return None


def loop_through_workouts(num: int=3):
    workouts = py_conn.GetRecentWorkouts(num)
    for w in workouts:
        df_workout = pd.json_normalize(w)
        workout_id = df_workout['id'].loc[0]
        
        ## Note that so far, you've just filled a bunch of variables; you haven't
        ## done anything with them yet!!!
               
        
        instructor = check_column('instructor_name', df_workout)[0]
        title = check_column('ride.title', df_workout)[0]
        duration = check_column('ride.duration', df_workout, alternate_column='ride.length')[0]
        length = check_column('ride.length', df_workout, alternate_column='ride.duration')[0] 
        difficulty = check_column('ride.difficulty_estimate', df_workout)[0] 
    
        workout_metrics_by_id_dict = py_conn.GetWorkoutMetricsById(workout_id)
        
        df_summaries = pd.json_normalize(workout_metrics_by_id_dict['summaries'])
        if 'value' in df_summaries.columns:
            output_total = check_row(0, 'value', df_summaries)
            distance = check_row(1, 'value', df_summaries)
            cals = check_row(2, 'value', df_summaries)
        
        df_average_summaries = pd.json_normalize(workout_metrics_by_id_dict['average_summaries'])
        if 'max_value' in df_average_summaries.columns:
            output_max = check_row(0, 'max_value', df_average_summaries)
            output_avg = check_row(0, 'average_value', df_average_summaries)
            cadence_max = check_row(1, 'max_value', df_average_summaries)
            cadence_avg = check_row(1, 'average_value', df_average_summaries)
            resistance_max = check_row(2, 'max_value', df_average_summaries)
            resistance_avg = check_row(2, 'average_value', df_average_summaries)
            speed_max = check_row(3, 'max_value',df_average_summaries)
            speed_avg = check_row(3, 'average_value', df_average_summaries)
            hr_max = check_row(4, 'max_value', df_average_summaries)
            hr_avg = check_row(4, 'average_value', df_average_summaries)
            
        if 'effort_zones' in workout_metrics_by_id_dict:
            df_effort_zones = pd.json_normalize(workout_metrics_by_id_dict['effort_zones'])
            
            total_effort_points = check_column('total_effort_points', df_effort_zones)[0]
            hr_zone1_duration = check_column('heart_rate_zone_durations.heart_rate_z1_duration', df_effort_zones)[0]
            hr_zone2_duration = check_column('heart_rate_zone_durations.heart_rate_z2_duration', df_effort_zones)[0]
            hr_zone3_duration = check_column('heart_rate_zone_durations.heart_rate_z3_duration', df_effort_zones)[0]
            hr_zone4_duration = check_column('heart_rate_zone_durations.heart_rate_z4_duration', df_effort_zones)[0]
        
        
if __name__ == "main":
    loop_through_workouts()
        
        
        
# with open('/home/zvaughan/python/peloton/src/sample.json') as json_data:
#     data = json.load(json_data)

# data = py_conn.GetWorkoutMetricsById('a28456ecb2564c7991037b0e9445bf1b')
# # data = py_conn.GetRecentWorkouts(1)
# df = pd.json_normalize(data)
# if asdoih != None:
#     print("woii")
# else:
#     print("noooooo")


# df.to_csv('/mnt/home-ds920/asdf9.csv')
        
# workouts = py_conn.GetRecentWorkouts(3)
# for w in workouts:
#     df_workout = pd.json_normalize(w)
#     workout_id = df_workout['id'].loc[0]
#     workout_metrics_by_id_dict = py_conn.GetWorkoutMetricsById(workout_id)
#     df_average_summaries = pd.json_normalize(workout_metrics_by_id_dict['average_summaries'])
#     df_summaries = pd.json_normalize(workout_metrics_by_id_dict['summaries'])
#     df_metrics = pd.json_normalize(workout_metrics_by_id_dict['metrics'])
#     df_effort_zones = pd.json_normalize(workout_metrics_by_id_dict['effort_zones'])
    
#     instructor = df_workout['instructor_name'].loc[0]
#     title = df_workout['ride.title'].loc[0]
#     duration = df_workout['ride.duration'].loc[0]
#     length = df_workout['ride.length'].loc[0]
    
#     output_total = df_summaries['value'].loc[0]
#     distance = df_summaries['value'].loc[1]
#     cals = df_summaries['value'].loc[2]
    
#     output_max = df_average_summaries['max_value'].loc[0]
#     output_avg = df_average_summaries['average_value'].loc[0]
#     cadence_max = df_average_summaries['max_value'].loc[1]
#     cadence_avg = df_average_summaries['average_value'].loc[1]
#     resistance_max = df_average_summaries['max_value'].loc[2]
#     resistance_avg = df_average_summaries['average_value'].loc[2]
#     speed_max = df_average_summaries['max_value'].loc[3]
#     speed_avg = df_average_summaries['average_value'].loc[3]
#     hr_max = df_average_summaries['max_value'].loc[4]
#     hr_avg = df_average_summaries['average_value'].loc[4]
        
# workouts = py_conn.GetRecentWorkouts(1)
# df = pd.json_normalize(workouts[0])
# df.to_csv('/mnt/home-ds920/asdf7.csv')

# df.to_csv('asdf.csv')

# print(json.dumps(data, indent=2))

# print(df)



# workouts = py_conn.GetRecentWorkouts(3)
# # print(json.dumps(workouts, indent=2))

# df = json_normalize(workouts[0])


# print(df.columns.to_series().to_string())
# print(df)
# df.to_csv('/mnt/home-ds920/asdf.csv')


'''
The upshot of all this testing?  
pd.json_normalize() should work on:
 - GetRecentWorkouts(new_workouts_num) (for each workout in the returned list)
 - These subcomponents of GetWorkoutMetricsById(workout_id):
   - 'average_summaries'
   - 'summaries'
   - 'metrics'
   - 'effort_zones'

So, therefore, try this:
'''

'''
workouts = py_conn.GetRecentWorkouts(new_workouts_num)
for w in workouts:
    df_workout = pd.json_normalize(w)
    workout_id = df_workout['id'].loc[0]
    df_
'''