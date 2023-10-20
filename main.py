import pandas as pd
import sqlalchemy as db
from pylotoncycle import pylotoncycle

import peloton.constants as const
import peloton.functions as func
import peloton.helpers as helpers
import peloton.peloton_pivots as pivots


def main():
    SQL_DB = "peloton"
    EXCEL_FILE = "/mnt/home-ds920/peloton_workouts.xlsx"

    py_conn = pylotoncycle.PylotonCycle(const.PELOTON_USERNAME, const.PELOTON_PASSWORD) 
        
    sql_engine = helpers.create_mariadb_engine(SQL_DB)

    # Pull raw workout data from MariaDB and use it to calculate the number of new Peloton workouts
    df_raw_workouts_data_in_sql = func.ingest_raw_workout_data_from_sql(sql_engine)
    new_workouts_num = func.calculate_new_workouts_num(py_conn, df_raw_workouts_data_in_sql)
    
    if new_workouts_num > 0:
        df_raw_workout_data_new = func.pull_new_raw_workouts_data_from_peloton(py_conn, df_raw_workouts_data_in_sql, new_workouts_num)

        df_raw_workout_metrics_data_new = func.pull_new_raw_metrics_data_from_peloton(py_conn, df_raw_workout_data_new)

        # Write the new raw data to MariaDB
        func.export_raw_workout_data_to_sql(df_raw_workout_data_new, sql_engine)
        func.export_raw_metrics_data_to_sql(df_raw_workout_metrics_data_new, sql_engine)
        
        # Process the new raw data
        df_processed = func.process_workouts_from_raw_data(df_raw_workout_data_new, df_raw_workout_metrics_data_new)

        # Write the new processed data to MariaDB
        func.export_processed_data_to_sql(df_processed, sql_engine)

    # Whether or not there are new workouts, pull the full processed dataset from MariaDB and print to terminal
    df_processed_workouts_data_in_sql = func.ingest_processed_data_from_sql(sql_engine)
    print(df_processed_workouts_data_in_sql)

    # Print pivot tables
    df_pivots = pivots.get_sql_data_for_pivots(sql_engine)  
    year_table = pivots.get_pivot_table_year(df_pivots)
    month_table = pivots.get_pivot_table_month(df_pivots)
    totals_table = pivots.get_grand_totals_table(year_table)
    
    print("")
    print(year_table)
    print("")
    print(month_table)
    print("")
    print("      GRAND TOTALS")
    print(totals_table.round(2))

    year_table.to_csv(f"{const.PELOTON_CSV_DIR}/year_table.csv")
    month_table.to_csv(f"{const.PELOTON_CSV_DIR}/month_table.csv")
    totals_table.to_csv(f"{const.PELOTON_CSV_DIR}/totals_table.csv")

       
if __name__ == "__main__":
    main()







    
    # mariadb_df = get_peloton_data_from_sql(sql_engine)

         
    # df_sql = select_all_from_table(sql_engine, SQL_TABLE, index_col=None, parse_dates=None)

    # print(df_sql)
    
    # If there are new workouts: retrieve the data, write to MariaDB, 
    #   re-pull from MariaDB, calculate new metrics, and write to Excel
    # new_workouts_num = calculate_new_workouts_num(py_conn, df_sql)
    
    # if new_workouts_num > 0:
    #     new_workouts_df = process_workouts(py_conn, new_workouts_num)
        
    #     export_peloton_data_to_sql(new_workouts_df, sql_engine)
            
    #     all_workouts_df = select_all_from_table(sql_engine, SQL_TABLE, index_col=None, parse_dates=None)

    #     # excel_df = calculate_excel_metrics(all_entries)

    #     # with pd.ExcelWriter(EXCEL_FILE, mode='a', if_sheet_exists='replace') as writer:
    #     #     excel_df.to_excel(writer, sheet_name='peloton_workouts', index=False, float_format='%.2f') 
            
    #     print("New workout data:")
    #     print(all_workouts_df)
    

    # df = zmv_peloton.process_workouts(py_conn, workouts_num=2)  ## might need to pull data in batches to avoid API timeout
    # print(df)    
    # df.to_csv(f"/mnt/home-ds920/asdf-{datetime.now().strftime('%Y-%m-%d %H-%M-%s')}.csv")
    
    # zmv_peloton.export_peloton_data_to_sql(df, sql_engine, "test")