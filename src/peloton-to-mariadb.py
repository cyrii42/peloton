import pandas as pd
from utils.pyloton_zmv import ingest_sql_data, calculate_new_workouts_num, \
    get_new_workouts, export_to_sql, calculate_excel_metrics

excel_filename = "/mnt/home-ds920/peloton_workouts.xlsx"

if __name__ == "__main__":

    # Pull MariaDB data and use it to calculate number of new Peloton workouts 
    mariadb_df = ingest_sql_data()

    # Use MariaDB data to calculate number of new Peloton workouts
    new_workouts_num = calculate_new_workouts_num(mariadb_df)

    # If there are new entries:
    if new_workouts_num > 0:
        # (1) retrieve new workout data
        new_entries = get_new_workouts(new_workouts_num)
        
        # (2) append DataFrame to MariaDB table
        export_to_sql(new_entries)
            
        # (3) Pull MariaDB data again, this time to create a new "all_entries" DataFrame
        all_entries = ingest_sql_data()

        # (4) calculate new metrics and append them to "all_entries" DataFrame
        excel_df = calculate_excel_metrics(all_entries)

        # (5) write Excel file
        with pd.ExcelWriter(excel_filename, mode='a', if_sheet_exists='replace') as writer:
            excel_df.to_excel(writer, sheet_name='peloton_workouts', index=False, float_format='%.2f') 
            
        # (6) print the new DataFrame to console
        print(all_entries)