from datetime import datetime
from pylotoncycle import pylotoncycle
from utils.constants import EASTERN_TIME, PELOTON_USERNAME, PELOTON_PASSWORD
import pandas as pd
import csv
import json
from pprint import pprint

# Create PylotonCycle connection object
py_conn = pylotoncycle.PylotonCycle(PELOTON_USERNAME, PELOTON_PASSWORD)

# # Get some recent workouts
# workouts = pd.Series(py_conn.GetRecentWorkouts(1))

# print(workouts.loc[0]['overall_summary'])
# print(workouts.columns)

# json_dict = {'created_at': 1695141644,'device_type': 'home_bike_v1', 'end_time': 1695143152, 'fitness_discipline': 'cycling', 'has_pedaling_metrics': True, 'has_leaderboard_metrics': False, 'id': 'fab09257a18b42c9b9db7b1e59a6a02a', 'is_total_work_personal_record': False, 'is_outdoor': False, 'metrics_type': 'cycling', 'name': 'Cycling Workout', 'peloton_id': None, 'platform': 'home_bike', 'start_time': 1695141644, 'status': 'COMPLETE', 'timezone': 'America/New_York', 'title': '25 min Just Ride', 'total_work': 177747.42, 'user_id': 'd181e93bdc6c42d3b388a8e72c3b62a6', 'workout_type': 'freestyle', 'total_video_watch_time_seconds': 0, 'total_video_buffering_seconds': 0, 'v2_total_video_watch_time_seconds': None, 'v2_total_video_buffering_seconds': None, 'total_music_audio_play_seconds': None, 'total_music_audio_buffer_seconds': None, 'service_id': None, 'created': 1695141644, 'device_time_created_at': 1695127244, 'strava_id': None, 'fitbit_id': None, 'is_skip_intro_available': False, 'pause_time_remaining': None, 'pause_time_elapsed': None, 'is_paused': False, 'has_paused': False, 'is_pause_available': True, 'pause_time_limit': 60.0, 'ride': {'id': '00000000000000000000000000000000', 'is_archived': False, 'title': '25 min Just Ride', 'scheduled_start_time': 1695141644, 'duration': 1508, 'instructor': {'name': 'JUST RIDE', 'image_url': 'https://s3.amazonaws.com/peloton-ride-images/just-ride-indoor.png'}}, 'achievement_templates': [], 'leaderboard_rank': None, 'total_leaderboard_users': 0, 'ftp_info': {'ftp': 0, 'ftp_source': None, 'ftp_workout_id': None}, 'device_type_display_name': 'Bike', 'overall_summary': {'created_at': 1695141644, 'device_type': 'home_bike_v1', 'end_time': 1695143152, 'fitness_discipline': 'cycling', 'has_pedaling_metrics': True, 'has_leaderboard_metrics': False, 'id': 'fab09257a18b42c9b9db7b1e59a6a02a', 'is_total_work_personal_record': False, 'is_outdoor': False, 'metrics_type': 'cycling', 'name': 'Cycling Workout', 'peloton_id': None, 'platform': 'home_bike', 'start_time': 1695141644, 'status': 'COMPLETE', 'timezone': 'America/New_York', 'title': '25 min Just Ride', 'total_work': 177747.42, 'user_id': 'd181e93bdc6c42d3b388a8e72c3b62a6', 'workout_type': 'freestyle', 'total_video_watch_time_seconds': 0, 'total_video_buffering_seconds': 0, 'v2_total_video_watch_time_seconds': None, 'v2_total_video_buffering_seconds': None, 'total_music_audio_play_seconds': None, 'total_music_audio_buffer_seconds': None, 'service_id': None, 'created': 1695141644, 'device_time_created_at': 1695127244, 'strava_id': None, 'fitbit_id': None, 'is_skip_intro_available': False, 'pause_time_remaining': None, 'pause_time_elapsed': None, 'is_paused': False, 'has_paused': False, 'is_pause_available': True, 'pause_time_limit': 60.0, 'ride': {'id': '00000000000000000000000000000000', 'is_archived': False, 'title': '25 min Just Ride', 'scheduled_start_time': 1695141644, 'duration': 1508, 'instructor': {'name': 'JUST RIDE', 'image_url': 'https://s3.amazonaws.com/peloton-ride-images/just-ride-indoor.png'}}, 'achievement_templates': [], 'leaderboard_rank': None, 'total_leaderboard_users': 0, 'ftp_info': {'ftp': 0, 'ftp_source': None, 'ftp_workout_id': None}, 'device_type_display_name': 'Bike'}, 'instructor_name': 'JUST RIDE'}

# pprint(json_dict)
  
workout_ids = [
    'fab09257a18b42c9b9db7b1e59a6a02a',
    # 'ed62ed7073c74c63926fd83d0cb8d17d',
    # '27b4f41677e244a88599a9517960b008',
    # '84a3f92f4254490e871c1297232df709',
] 

list = []
for w in workout_ids:
    list.append(pd.Series(py_conn.GetWorkoutMetricsById(w)))
    
df = pd.DataFrame(list)

print(df.columns)
print(df.to_string())
  
# workout_metrics = py_conn.GetWorkoutMetricsById('fab09257a18b42c9b9db7b1e59a6a02a')
# workout_metrics_json = json.dumps(workout_metrics, sort_keys=True, indent=2)
# print(workout_metrics_json)
  
# workout_summary = py_conn.GetWorkoutMetricsById('fab09257a18b42c9b9db7b1e59a6a02a')
# workout_summary_json = json.dumps(workout_summary, sort_keys=True, indent=2)
# print(workout_summary_json)

# with open('sample.json') as user_file:
#   file_contents = user_file.read()

# workout_metrics_json = json.loads(file_contents)

# pprint.pprint(workout_metrics_json)


'''
WORKOUT IDs:
fab09257a18b42c9b9db7b1e59a6a02a
ed62ed7073c74c63926fd83d0cb8d17d
27b4f41677e244a88599a9517960b008
84a3f92f4254490e871c1297232df709
d8ec1d740a0145afb2b3b9dd5697dd82
'''
      
# csv_filename = '/mnt/home-ds920/workouts.csv'

# workouts.to_csv(csv_filename)