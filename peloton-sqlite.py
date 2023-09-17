## Potential useful questions to answer
# how long since last workout?
# how many workouts per week over last X weeks?
# average calorie burn (or whatever) over last X rides?

import pandas as pd
from config import mariadb_conn
from get_workout_info import get_workout_dict, get_new_workouts_num

# Create Pandas DataFrame from existing table
with mariadb_conn as conn:
    db_dataframe = pd.read_sql("SELECT * from peloton", conn, index_col='start_time_iso', parse_dates=['start_time_iso', 'start_time_local'])

# Calculate number of new workouts not yet in DB
new_workouts = get_new_workouts_num(db_dataframe)

# Retrieve new workouts (if any) from Peloton and create Pandas DataFrame from dict of lists
new_entries = get_workout_dict(new_workouts)

# If there are new entries:
#   (i)    append DataFrame to MariaDB table
#   (ii)   create new, concatenated "all_entries" DataFrame;
#   (iii)  calculate new metrics and append to "all_entries" DataFrame; and
#   (iv)   write Excel file
if new_entries.shape[0] > 0:
    with mariadb_conn as conn:
        new_entries.to_sql("peloton", conn, if_exists="append", index=False)
        
    all_entries = pd.concat([db_dataframe, new_entries], ignore_index=True)

    duration_list = all_entries['duration'].tolist()
    length_list = all_entries['length'].tolist()
    output_list = all_entries['output'].tolist()
    all_entries['duration_min'] = [(x / 60) for x in duration_list]
    all_entries['length_min'] = [(x / 60) for x in length_list]
    all_entries['output_per_min'] = [(x[0] / (x[1] / 60)) for x in zip(output_list, duration_list)]

    with pd.ExcelWriter('/mnt/home-ds920/peloton_workouts.xlsx', mode='a', if_sheet_exists='replace') as writer:
        all_entries.to_excel(writer, sheet_name='peloton_workouts', index=False, float_format='%.2f')

# Print the final DataFrame
if new_entries.shape[0] > 0:
    print(new_entries)
else:
    print(db_dataframe)






# if new_entries.shape[0] > 0:
#     all_entries = pd.concat([db_dataframe, new_entries], ignore_index=True) 
# else:
#     all_entries = db_dataframe
#     print(all_entries.tail)



# start_datetime = datetime.fromtimestamp(start_timestamp, tz=eastern_time)
# peloton_dict['start_time'].append(start_datetime)
# start_iso = start_datetime.isoformat(sep='T')