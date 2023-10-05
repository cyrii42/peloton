'''
    ########## consider creating multiple SQL tables for stuff like 
    ##########  splits data, and joining them together!!!
    
    other ideas for further improvement:
    
    - loop through ALL Pyloton functions and dump ALL raw data to MariaDB 
        (with workout_id) as the index/primary key
    
    - make multiple other tables, each with the workout_id as the index/primary key
        - ride mile splits
        - output, speed, resistance for each minute (in metrics/metrics JSON)
        
        - subcategories to examine from GetWorkoutMetricsById (see "metrics-10am.csv"):
            - average_summaries
            - summaries
            - metrics
                - values (in output, cadence, resistance, and heart rate)
                - zones (in heart rate)
                
            - effort_zones
            
            - segment_list
            - seconds_since_pedaling_start
            - muscle_group_score
            - splits_data

                - splits
            - splits_metrics
                - header
                - metrics
                    - data (in each sub-unit)
            - target_performance_metrics
                - target_graph_metrics
                    - upper, lower, average (in each sub-unit)

            - target_metrics_performance_data
                - target_metrics
                    - metrics (in each sub-unit)
                - time_in_metric
    
    - learn about SQL/Pandas "join" functions
    
'''

from datetime import datetime
from pylotoncycle import pylotoncycle
import peloton.constants as const
import peloton.helpers as helpers
import peloton.functions as zmv_peloton
 

def main():
    SQL_DB = "peloton"
    SQL_TABLE = "test"
    EXCEL_FILE = "/mnt/home-ds920/peloton_workouts.xlsx"

    py_conn = pylotoncycle.PylotonCycle(const.PELOTON_USERNAME, const.PELOTON_PASSWORD) 
        
    sql_engine = helpers.create_mariadb_engine(SQL_DB)
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
    

    df = zmv_peloton.process_workouts(py_conn, workouts_num=2)  ## might need to pull data in batches to avoid API timeout
    print(df)    
    df.to_csv(f"/mnt/home-ds920/asdf-{datetime.now().strftime('%Y-%m-%d %H-%M-%s')}.csv")
    
    # zmv_peloton.export_peloton_data_to_sql(df, sql_engine, "test")
    

        
if __name__ == "__main__":
    main()
