
################################################################################
################################################################################
###################### COMMENT JUNKYARD STARTS HERE ############################
################################################################################
################################################################################









    

    # (df_raw_workout_data_new, df_raw_workout_metrics_data_new) = pull_new_raw_data_from_peloton(py_conn, 3)

    # # print(df_raw_workout_data_new)
    # # print("")
    # # print(df_raw_workout_metrics_data_new)

    # df_processed = process_workouts_from_raw_pyloton_data(df_raw_workout_data_new, df_raw_workout_metrics_data_new)

    # print(df_processed)

    # filename_out_workouts_processed = str(datetime.now().strftime("%Y-%m-%d_%H-%M")) + "_peloton_raw_data_metrics.csv"
    # filename_out_metrics_processed = str(datetime.now().strftime("%Y-%m-%d_%H-%M")) + "_peloton_raw_data_metrics.csv"

    # df_raw_workout_data_for_processing = ingest_raw_workout_data_from_sql(sql_engine).reset_index()
    # df_raw_metrics_data_for_processing = ingest_raw_metrics_data_from_sql(sql_engine).reset_index()

    # df_processed = process_workouts_from_raw_data(df_raw_workout_data_for_processing, df_raw_metrics_data_for_processing)
    # print(df_processed)
    # filename_out_processed = str(datetime.now().strftime("%Y-%m-%d_%H-%M")) + "_peloton_processed_data.csv"

    # df_processed.to_csv(filename_out_processed, index=False, index_label='id')

    # export_processed_data_to_sql(df_processed, sql_engine)

    ##### VARIABLES FOR AN INITIAL WRITE OF DATA TO SQL FROM CSV FILES###############
    # df_workouts_first_time = pd.read_csv("2023-10-04_22-16_peloton_raw_data_workouts.csv", index_col=0)
    # export_raw_workout_data_to_sql(df_workouts_first_time, sql_conn)

    # df_workout_metrics_first_time = pd.read_csv("2023-10-05_11-25_peloton_raw_data_metrics.csv", index_col=0)
    # export_raw_metrics_data_to_sql(df_workout_metrics_first_time, sql_conn)
    ####################################################################################

    # df_workouts_existing = pd.read_csv("2023-10-04_22-16_peloton_raw_data_workouts.csv", index_col=0)
    # df_workout_metrics_existing = pd.read_csv("2023-10-05_11-25_peloton_raw_data_metrics.csv", index_col=0)

    # new_workouts_num = calculate_new_workouts_num(py_conn, df_workouts_existing)

    # if new_workouts_num > 0:
    #     (df_workouts_new, df_workout_metrics_new) = pull_new_raw_data_from_peloton(py_conn, new_workouts_num)

    #     ##### Add something here to WRITE the new raw data to CSV / MariaDB

    #     df_processed = process_workouts_from_raw_data(df_workouts_new, df_workout_metrics_new)

    #     ##### Add something here to WRITE the new processed data to CSV / MariaDB

    # process_workouts_from_raw_data()
    # filename_out_workouts_processed = str(datetime.now().strftime("%Y-%m-%d_%H-%M")) + "_peloton_raw_data_metrics.csv"
    # filename_out_metrics_processed = str(datetime.now().strftime("%Y-%m-%d_%H-%M")) + "_peloton_raw_data_metrics.csv"

    # print(get_total_workouts_num(py_conn))

    # random_str_list = [random.randint(100000, 999999) for x in range(170)]
    # split_workout_ids_into_groups(random_str_list)

    # get_full_list_of_workout_ids(py_conn, 170)

    # get_full_list_of_workout_ids_from_csv("workout_ids.csv")

    # workout_ids_list = get_full_list_of_workout_ids_from_csv("workout_ids.csv")
    # workout_ids_list_of_lists = split_workout_ids_into_groups(workout_ids_list)

    # filename_out_workouts = str(datetime.now().strftime("%Y-%m-%d_%H-%M")) + "_peloton_raw_data_workouts.csv"
    # workouts_df = pull_all_raw_workout_data_from_peloton(py_conn, 170)
    # print(workouts_df)
    # workouts_df.to_csv(filename_out_workouts)

    # filename_out_metrics = str(datetime.now().strftime("%Y-%m-%d_%H-%M")) + "_peloton_raw_data_metrics.csv"
    # workout_metrics_df = pull_all_raw_metrics_data_from_peloton(py_conn, workout_ids_list_of_lists)
    # print(workout_metrics_df)
    # workout_metrics_df.to_csv(filename_out_metrics)

    # workouts_df = pd.read_csv("2023-10-04_22-16_peloton_raw_data_workouts.csv", index_col=0)
    # workout_metrics_df = pd.read_csv("2023-10-04_22-34_peloton_raw_data_metrics.csv", index_col=0)

    # df_combined = combine_workout_dataframes(workouts_df, workout_metrics_df)

    # print(df_combined)

    # filename_out_combined = str(datetime.now().strftime("%Y-%m-%d_%H-%M")) + "_peloton_raw_data_combined.csv"

    # df_combined.to_csv(filename_out_combined)

    # for index, workout_series in df_workouts.iterrows():
    #     workout_id = workout_series['id']
    #     ride_attributes_dict = {}

    #     workout_metrics_series = df_workout_metrics.loc[workout_id]
    # # Set "Strive Score" attribute & loop through HR Zone Duration columns
    #     if workout_metrics_series.notna()['effort_zones']:
    #         df_effort_zones = pd.json_normalize(ast.literal_eval(workout_metrics_series['effort_zones']))
    #         # df_hr_zone_durations = pd.json_normalize(ast.literal_eval(workout_metrics_series['effort_zones']['heart_rate_zone_durations']))

    #         ride_attributes_dict.update({ "strive_score": df_effort_zones['total_effort_points'][0] })
    #         for x in range(4):
    #             zone_num = x + 1
    #             column_name = f"heart_rate_zone_durations.heart_rate_z{zone_num}_duration"
    #             ride_attributes_dict.update({ column_name: df_effort_zones[column_name][0] })

    #     print(ride_attributes_dict)

    # for index, workout_series in df_workouts.iterrows():
    #     workout_id = workout_series['id']
    #     workout_metrics_series = df_workout_metrics.loc[workout_id]
    #     print(workout_metrics_series)

    # ride_series = pd.Series(workouts_df['ride'])
    # ride_string = ast.literal_eval(ride_series[0])
    # print(pd.json_normalize(ride_string))

    # if workout_metrics_df.notna()['effort_zones']:
    #     df_effort_zones = pd.json_normalize(ast.literal_eval(workout_metrics_df['effort_zones']))
    #     df_hr_zone_durations = pd.json_normalize(ast.literal_eval(workout_metrics_df['effort_zones']['heart_rate_zone_durations']))
    #     print(df_effort_zones)
    #     print(df_hr_zone_durations)

    # for index, df_metrics_row in workout_metrics_df.iterrows():
    #     # if 'effort_zones' in df_metrics_row.index.values:
    #     if df_metrics_row.notna()['effort_zones']:
    #         effort_zones_df = pd.json_normalize(ast.literal_eval(df_metrics_row['effort_zones']))
    #         for index, item in effort_zones_df.items():
    #             print(item)

    # all_workout_ids = get_full_list_of_workout_ids_from_csv("workout_ids.csv")

    # workout_ids_list_of_lists = split_workout_ids_into_groups(all_workout_ids)

    # metrics_df = pull_all_raw_metrics_data_from_peloton(py_conn, workout_ids_list_of_lists)

    # print(metrics_df)

    # filename_out_metrics = str(datetime.now().strftime("%Y-%m-%d_%H-%M")) + "_peloton_raw_data_metrics.csv"

    # metrics_df.to_csv(filename_out_metrics)

    # existing_workouts_df = pd.read_csv("2023-10-04_22-16_peloton_raw_data_workouts.csv", index_col=0)
    # existing_workout_metrics_df = pd.read_csv("2023-10-04_22-34_peloton_raw_data_metrics.csv", index_col=0)

    # new_workouts_num = calculate_new_workouts_num(py_conn, existing_workouts_df)

    # if new_workouts_num > 0:
    #     df_tuple = pull_new_raw_data_from_peloton(py_conn, new_workouts_num)
    #     new_workouts_df = df_tuple[0]
    #     new_workout_metrics_df = df_tuple[1]
    #     print(new_workouts_df)
    #     print("")
    #     print(new_workout_metrics_df)
    # else:
    #     print(existing_workouts_df)
    #     print("")
    #     print(existing_workout_metrics_df)












    
    # workouts = py_conn.GetWorkoutMetricsById("1549b39e75cb48c0ac6179b952ce2cac")
    # df = pd.json_normalize(workouts['metrics'])
    # df1 = df.set_index('slug')
    # print(df1['max_value'])
    # # df.to_csv(f"/mnt/home-ds920/asdf-{datetime.now().strftime('%H-%M-%s')}.csv")
        
        
        
        # ride_object.created_at = check_column('created_at', df_workout)[0]  
        # ride_object.start_time = check_column('start_time', df_workout)[0]   
        # ride_object.end_time = check_column('end_time', df_workout)[0]      
        # ride_object.user_id = check_column('user_id', df_workout)[0]
        # ride_object.instructor = check_column('instructor_name', df_workout)[0]
        # ride_object.timezone = check_column('timezone', df_workout)[0]
        # ride_object.total_work = check_column('total_work', df_workout)[0]   
        # ride_object.has_pedaling_metrics = check_column('has_pedaling_metrics', df_workout)[0]
        # ride_object.has_leaderboard_metrics = check_column('has_leaderboard_metrics', df_workout)[0]
        # ride_object.metrics_type = check_column('metrics_type', df_workout)[0]
        # ride_object.workout_type = check_column('workout_type', df_workout)[0]   
        # ride_object.average_effort_score = check_column('average_effort_score', df_workout)[0]  
        # ride_object.leaderboard_rank = check_column('leaderboard_rank', df_workout)[0]    
        # ride_object.total_leaderboard_users = check_column('total_leaderboard_users', df_workout)[0]
    
        # ride_object.title = check_column('ride.title', df_workout)[0]
        # ride_object.description = check_column('ride.description', df_workout)[0]
        # ride_object.duration = check_column('ride.duration', df_workout, alternate_column='ride.length')[0]
        # ride_object.length = check_column('ride.length', df_workout, alternate_column='ride.duration')[0] 
        # ride_object.difficulty = check_column('ride.difficulty_estimate', df_workout)[0] 
        # ride_object.ride_id = check_column('ride.id', df_workout)[0]
        # ride_object.ride_image_url = check_column('ride.image_url', df_workout)[0]
        
# # with open('/home/zvaughan/python/peloton/src/sample.json') as json_data:
# #     data = json.load(json_data)

# # data = py_conn.GetWorkoutMetricsById('a28456ecb2564c7991037b0e9445bf1b')
# # # data = py_conn.GetRecentWorkouts(1)
# # df = pd.json_normalize(data)
# # if asdoih != None:
# #     print("woii")
# # else:
# #     print("noooooo")



        
        # df_summaries = pd.json_normalize(workout_metrics_by_id_dict['summaries'])
        # for row in df_summaries:
            
        # if 'value' in df_summaries.columns:
        
        #     ride_object.output_total = check_row(0, 'value', df_summaries)
        #     ride_object.distance = check_row(1, 'value', df_summaries)
        #     ride_object.calories_total = check_row(2, 'value', df_summaries)
        
        # df_average_summaries = pd.json_normalize(workout_metrics_by_id_dict['average_summaries'])
        # if 'max_value' in df_average_summaries.columns:
        #     ride_object.output_avg = check_row(0, 'average_value', df_average_summaries)
        #     ride_object.output_max = check_row(0, 'max_value', df_average_summaries)
        #     ride_object.cadence_avg = check_row(1, 'average_value', df_average_summaries)
        #     ride_object.cadence_max = check_row(1, 'max_value', df_average_summaries)
        #     ride_object.resistance_avg = check_row(2, 'average_value', df_average_summaries)
        #     ride_object.resistance_max = check_row(2, 'max_value', df_average_summaries)
        #     ride_object.speed_avg = check_row(3, 'average_value', df_average_summaries)
        #     ride_object.speed_max = check_row(3, 'max_value',df_average_summaries)
        #     ride_object.hr_avg = check_row(4, 'average_value', df_average_summaries)
        #     ride_object.hr_max = check_row(4, 'max_value', df_average_summaries)
            
        # if 'effort_zones' in workout_metrics_by_id_dict:
        #     df_effort_zones = pd.json_normalize(workout_metrics_by_id_dict['effort_zones'])
            
        #     ride_object.strive_score = check_column('total_effort_points', df_effort_zones)[0]
        #     ride_object.hr_zone1_duration = check_column('heart_rate_zone_durations.heart_rate_z1_duration', df_effort_zones)[0]
        #     ride_object.hr_zone2_duration = check_column('heart_rate_zone_durations.heart_rate_z2_duration', df_effort_zones)[0]
        #     ride_object.hr_zone3_duration = check_column('heart_rate_zone_durations.heart_rate_z3_duration', df_effort_zones)[0]
        #     ride_object.hr_zone4_duration = check_column('heart_rate_zone_durations.heart_rate_z4_duration', df_effort_zones)[0]
            
        # print(ride_object)

# # df.to_csv('/mnt/home-ds920/asdf9.csv')
        
# # workouts = py_conn.GetRecentWorkouts(3)
# # for w in workouts:
# #     df_workout = pd.json_normalize(w)
# #     workout_id = df_workout['id'].loc[0]
# #     workout_metrics_by_id_dict = py_conn.GetWorkoutMetricsById(workout_id)
# #     df_average_summaries = pd.json_normalize(workout_metrics_by_id_dict['average_summaries'])
# #     df_summaries = pd.json_normalize(workout_metrics_by_id_dict['summaries'])
# #     df_metrics = pd.json_normalize(workout_metrics_by_id_dict['metrics'])
# #     df_effort_zones = pd.json_normalize(workout_metrics_by_id_dict['effort_zones'])
    
# #     instructor = df_workout['instructor_name'].loc[0]
# #     title = df_workout['ride.title'].loc[0]
# #     duration = df_workout['ride.duration'].loc[0]
# #     length = df_workout['ride.length'].loc[0]
    
# #     output_total = df_summaries['value'].loc[0]
# #     distance = df_summaries['value'].loc[1]
# #     cals = df_summaries['value'].loc[2]
    
# #     output_max = df_average_summaries['max_value'].loc[0]
# #     output_avg = df_average_summaries['average_value'].loc[0]
# #     cadence_max = df_average_summaries['max_value'].loc[1]
# #     cadence_avg = df_average_summaries['average_value'].loc[1]
# #     resistance_max = df_average_summaries['max_value'].loc[2]
# #     resistance_avg = df_average_summaries['average_value'].loc[2]
# #     speed_max = df_average_summaries['max_value'].loc[3]
# #     speed_avg = df_average_summaries['average_value'].loc[3]
# #     hr_max = df_average_summaries['max_value'].loc[4]
# #     hr_avg = df_average_summaries['average_value'].loc[4]
        
# # workouts = py_conn.GetWorkoutMetricsById("1549b39e75cb48c0ac6179b952ce2cac")
# # df = pd.json_normalize(workouts['splits_data']['splits'])
# # df.to_csv('/mnt/home-ds920/asdf999.csv')

# # df.to_csv('asdf.csv')

# # print(json.dumps(data, indent=2))

# # print(df)



# # workouts = py_conn.GetRecentWorkouts(3)
# # # print(json.dumps(workouts, indent=2))

# # df = json_normalize(workouts[0])


# # print(df.columns.to_series().to_string())
# # print(df)
# # df.to_csv('/mnt/home-ds920/asdf.csv')


# '''
# The upshot of all this testing?  
# pd.json_normalize() should work on:
#  - GetRecentWorkouts(new_workouts_num) (for each workout in the returned list)
#  - These subcomponents of GetWorkoutMetricsById(workout_id):
#    - 'average_summaries'
#    - 'summaries'
#    - 'metrics'
#    - 'effort_zones'

# So, therefore, try this:
# '''

# '''
# workouts = py_conn.GetRecentWorkouts(new_workouts_num)
# for w in workouts:
#     df_workout = pd.json_normalize(w)
#     workout_id = df_workout['id'].loc[0]
#     df_
# '''

# from decimal import Decimal, getcontext

# getcontext().prec = 4

# print(getcontext())
# print(Decimal('3434832.417') + Decimal(0))

# @dataclass
# class DCTest:
#     name: str = None
#     value: Decimal = None 
#     value2: Decimal = None
    
# dc_test1 = DCTest('bobby jones', 42)
# dc_test2 = DCTest('billy ray', 42.524, 99)
# dc_test3 = DCTest()
# dc_test3.name = 'betty sue'
# dc_test3.value = 5582.34

# print(dc_test1)
# print(dc_test2)
# print(dc_test1.value + dc_test2.value)
# print(type(dc_test2.value))
# print(dc_test3)

    

# # Check if specified column (or alternate column) exists in DataFrame; if so, return full column (as a Series)
# def check_column(column: str, df: pd.DataFrame, alternate_column: str=None):
#     if column in df.columns:
#         return df[column]
#     elif alternate_column in df.columns:
#         return df[alternate_column]
#     else:
#         if alternate_column == None:
#             print(f"Columnn {column} does not exist!")
#         else:
#             print(f"Neither column {column} nor column {alternate_column} exists!")
#         return None
    
    
# # Check if specified row number exists; if so, return the value of that row in specified column
# def check_row(row: int, column: str, df: pd.DataFrame) -> pd.Series | None:
#     if row < df.shape[0]:
#         return df[column][row]
#     else:
#         print(f"Row #{row} does not exist!")
#         return None