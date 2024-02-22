from datetime import datetime

import peloton.helpers as helpers
import pandas as pd
import trash.peloton_pivots as pivots
import sqlalchemy as db
from pylotoncycle import pylotoncycle

from peloton.constants import EASTERN_TIME, PELOTON_PASSWORD, PELOTON_USERNAME


# Calculate number of new workouts not yet in DB
def calculate_new_workouts_num(py_conn: pylotoncycle.PylotonCycle, df_input: pd.DataFrame) -> int:
    total_workouts = py_conn.GetMe()["total_workouts"]
    existing_workouts = df_input.shape[0]
    new_workouts = total_workouts - existing_workouts

    print("Total Workouts: " + str(total_workouts))
    print("Workouts in Database: " + str(existing_workouts))
    print("New Workouts to Write: " + str(new_workouts))
    
    return new_workouts


# Retrieve new workouts (if any) from Peloton and create Pandas DataFrame from dict of lists
def get_new_workouts(py_conn: pylotoncycle.PylotonCycle, new_workouts_num: int) -> pd.DataFrame:
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
            start_time_iso = datetime.fromtimestamp(start_timestamp, tz=EASTERN_TIME).isoformat(sep='T')
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


# Calculate new metrics for Excel sheet and output DataFrame
def calculate_excel_metrics(input_df: pd.DataFrame) -> pd.DataFrame:
    all_entries = input_df
    
    duration_list = all_entries['duration'].tolist()
    length_list = all_entries['length'].tolist()
    output_list = all_entries['output'].tolist()
    
    all_entries['duration_min'] = [(x / 60) for x in duration_list]
    all_entries['length_min'] = [(x / 60) for x in length_list]
    all_entries['output_per_min'] = [(x[0] / (x[1] / 60)) for x in zip(output_list, duration_list)]
    
    return all_entries


def main():
    EXCEL_FILENAME = "/mnt/home-ds920/peloton_workouts.xlsx"
    
    mariadb_engine = helpers.create_mariadb_engine(database="zmv")
    py_conn = pylotoncycle.PylotonCycle(PELOTON_USERNAME, PELOTON_PASSWORD)

    mariadb_df = helpers.get_peloton_data_from_sql(mariadb_engine)

    # If there are new workouts: retrieve the data, write to MariaDB, 
    #   re-pull from MariaDB, calculate new metrics, and write to Excel
    new_workouts_num = calculate_new_workouts_num(py_conn, mariadb_df)
    if new_workouts_num > 0:
        new_entries = get_new_workouts(py_conn, new_workouts_num)
        
        helpers.export_peloton_data_to_sql(new_entries, mariadb_engine)
            
        all_entries = helpers.get_peloton_data_from_sql(mariadb_engine)

        excel_df = calculate_excel_metrics(all_entries)

        with pd.ExcelWriter(EXCEL_FILENAME, mode='a', if_sheet_exists='replace') as writer:
            excel_df.to_excel(writer, sheet_name='peloton_workouts', index=False, float_format='%.2f') 
            
        print("New workout data:")
        print(all_entries)
            
    pivot_df = pivots.get_sql_data_for_pivots(mariadb_engine)
    year_table = pivots.get_pivot_table_year(pivot_df)
    month_table = pivots.get_pivot_table_month(pivot_df)

    print()
    print(year_table)
    print()
    print(month_table.drop(columns=["annual_periods", "monthly_periods"]))
    
    
if __name__ == "__main__":
    main()