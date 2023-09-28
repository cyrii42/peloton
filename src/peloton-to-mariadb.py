import pandas as pd
from utils.pyloton_zmv import ingest_sql_data, calculate_new_workouts_num, \
    get_new_workouts, export_to_sql, calculate_excel_metrics
from utils.peloton_pivots import get_pivot_table_year, get_pivot_table_month

def main():
    excel_filename = "/mnt/home-ds920/peloton_workouts.xlsx"

    # Pull MariaDB data and use it to calculate number of new Peloton workouts 
    mariadb_df = ingest_sql_data()

    # Use MariaDB data to calculate number of new Peloton workouts
    new_workouts_num = calculate_new_workouts_num(mariadb_df)

    # If there are new workouts: retrieve the data, write to MariaDB, 
    #   re-pull from MariaDB, calculate new metrics, and write to Excel
    if new_workouts_num > 0:
        new_entries = get_new_workouts(new_workouts_num)
        
        export_to_sql(new_entries)
            
        all_entries = ingest_sql_data()

        excel_df = calculate_excel_metrics(all_entries)

        with pd.ExcelWriter(excel_filename, mode='a', if_sheet_exists='replace') as writer:
            excel_df.to_excel(writer, sheet_name='peloton_workouts', index=False, float_format='%.2f') 
            
        print("New workout data:")
        print(all_entries)
            
    year_table = get_pivot_table_year()
    month_table = get_pivot_table_month()

    print()
    print(year_table.round(2))
    print()
    print(month_table.drop(columns=["annual_periods", "monthly_periods"]).round(2))
    
    
if __name__ == "__main__":
    main()