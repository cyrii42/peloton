import pandas as pd
from config import mariadb_conn
import zmv_pyloton

# Create Pandas DataFrame from existing table
with mariadb_conn as conn:
    mariadb_df = pd.read_sql("SELECT * from peloton", conn, index_col='start_time_iso', parse_dates=['start_time_iso', 'start_time_local'])

# Use MariaDB data to calculate number of new Peloton workouts 
new_workouts_num = zmv_pyloton.calculate_new_workouts_num(mariadb_df)

# If there are new entries:
if new_workouts_num > 0:
    # (1) retrieve new workout data
    new_entries = zmv_pyloton.get_new_workouts(new_workouts_num)
    
    # (2) append DataFrame to MariaDB table
    with mariadb_conn as conn:
        new_entries.to_sql("peloton", conn, if_exists="append", index=False)
        
    # (3) create new, concatenated "all_entries" DataFrame
    all_entries = pd.concat([mariadb_df, new_entries], ignore_index=True)

    # (4) calculate new metrics and append them to "all_entries" DataFrame
    duration_list = all_entries['duration'].tolist()
    length_list = all_entries['length'].tolist()
    output_list = all_entries['output'].tolist()
    all_entries['duration_min'] = [(x / 60) for x in duration_list]
    all_entries['length_min'] = [(x / 60) for x in length_list]
    all_entries['output_per_min'] = [(x[0] / (x[1] / 60)) for x in zip(output_list, duration_list)]

    # (5) write Excel file
    with pd.ExcelWriter('/mnt/home-ds920/peloton_workouts.xlsx', mode='a', if_sheet_exists='replace') as writer:
        all_entries.to_excel(writer, sheet_name='peloton_workouts', index=False, float_format='%.2f')


# OPTIONAL FOR TESTING: Print the final DataFrame
if new_workouts_num > 0:
    print(new_entries)
else:
    print(mariadb_df)