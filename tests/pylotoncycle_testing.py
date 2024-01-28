from datetime import datetime
from pprint import pprint

import constants as const
import pandas as pd
from pylotoncycle import pylotoncycle

py_conn = pylotoncycle.PylotonCycle(const.PELOTON_USERNAME, const.PELOTON_PASSWORD) 
TEST_ID = '7c32268e13784898aa617d4a610edfb6'

def print_recent_workouts():
    recent_workouts = py_conn.GetRecentWorkouts(2)
    pprint(recent_workouts[0]['ride'])

def print_metrics_for_id():
    '''
        duration:  <class 'int'>
        is_class_plan_shown:  <class 'bool'>
        segment_list:  <class 'list'>  (length 3)
        seconds_since_pedaling_start:  <class 'list'>  (length 25)
        average_summaries:  <class 'list'>  (length 4)
        summaries:  <class 'list'>  (length 3)
        metrics:  <class 'list'>  (length 5)
        has_apple_watch_metrics:  <class 'bool'>
        location_data:  <class 'list'>  (length 0)
        is_location_data_accurate:  <class 'NoneType'>
        splits_data:  <class 'dict'>
            splits_data / distance_marker_display_unit:  <class 'str'>
            splits_data / elevation_change_display_unit:  <class 'str'>
            splits_data / splits:  <class 'list'>
        splits_metrics:  <class 'dict'>
            splits_metrics / header:  <class 'list'>
            splits_metrics / metrics:  <class 'list'>
        target_performance_metrics:  <class 'dict'>
            target_performance_metrics / target_graph_metrics:  <class 'list'>
            target_performance_metrics / cadence_time_in_range:  <class 'int'>
            target_performance_metrics / resistance_time_in_range:  <class 'int'>
        target_metrics_compliance:  <class 'dict'>
        target_metrics_performance_data:  <class 'dict'>
            target_metrics_performance_data / target_metrics:  <class 'list'>
            target_metrics_performance_data / time_in_metric:  <class 'list'>
        effort_zones:  <class 'dict'>
            effort_zones / total_effort_points:  <class 'float'>
            effort_zones / heart_rate_zone_durations:  <class 'dict'>
        muscle_group_score:  <class 'list'>  (length 9)

        

        
        
        
    '''
    metrics_for_test_id = py_conn.GetWorkoutMetricsById(TEST_ID)

    # for key, val in metrics_for_test_id.items():
    #     if type(val) == dict:
    #         pass
    #         # for key1, val1 in val.items():
    #         #     print(f"{key} / {key1}:  {type(val1)}")
    #     elif type(val) == list:
    #         print(f"{key}:  list of length {len(val)}")

    print(type(pd.json_normalize(metrics_for_test_id)['segment_list'][0]))


def main():
    print_metrics_for_id()

if __name__ == '__main__':
    main()
