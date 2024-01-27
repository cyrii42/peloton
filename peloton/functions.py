import pandas as pd
import pylotoncycle

from peloton.raw_data_tests import (process_workouts_from_raw_data,
                                    pull_new_raw_data_from_peloton,
                                    pull_new_raw_metrics_data_from_peloton,
                                    pull_new_raw_workouts_data_from_peloton)


# Calculate number of new workouts not yet in DB
def calculate_new_workouts_num(py_conn: pylotoncycle.PylotonCycle, df_input: pd.DataFrame) -> int:
    total_workouts = py_conn.GetMe()["total_workouts"]
    existing_workouts = df_input.shape[0]
    new_workouts = total_workouts - existing_workouts

    print(f"Total Workouts: {total_workouts}")
    print(f"Workouts in Database: {existing_workouts}")
    print(f"New Workouts to Write: {new_workouts}")

    return new_workouts


