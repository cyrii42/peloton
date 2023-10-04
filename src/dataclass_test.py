# GetWorkoutList(self, num_workouts=None)
# GetWorkoutSummaryById(self, workout_id)
# GetWorkoutById(self, workout_id)
# GetInstructorById(self, instructor_id)
# GetFollowersById(self, userid=None)

import pandas as pd
import sqlalchemy as db
import inspect
from dataclasses import dataclass
from typing import List
from datetime import datetime
from pylotoncycle import pylotoncycle
from zoneinfo import ZoneInfo
from utils.constants import EASTERN_TIME, PELOTON_USERNAME, PELOTON_PASSWORD, \
    MARIADB_USER, MARIADB_PASS, MARIADB_SERVER
 

@dataclass
class PelotonRide:
    id: str = None
    start_time: int = None
    start_time_iso: str = None
    end_time: int = None
    end_time_iso: str = None
    ride_title: str = None
    instructor_name: str = None
    ride_instructor_id: str = None
    ride_description: str = None
    user_id: str = None
    ride_id: str = None
    ride_image_url: str = None
    timezone: str = None
    metrics_type: str = None
    total_work: float = None
    has_pedaling_metrics: str = None
    has_leaderboard_metrics: str = None
    workout_type: str = None
    average_effort_score: float = None
    leaderboard_rank: int = None
    total_leaderboard_users: int = None
    ride_duration: int = None
    ride_length: int = None
    distance: float = None
    ride_difficulty_estimate: float = None
    calories: float = None
    total_output: float = None
    output_avg: int = None
    output_max: int = None
    cadence_avg: int = None
    cadence_max: int = None
    resistance_avg: int = None
    resistance_max: int = None
    speed_avg: float = None
    speed_max: float = None
    heart_rate_avg: int = None
    heart_rate_max: int = None
    strive_score: float = None
    heart_rate_z1_duration: int = None
    heart_rate_z2_duration: int = None
    heart_rate_z3_duration: int = None
    heart_rate_z4_duration: int = None
    heart_rate_z5_duration: int = None
    
    # adapted from:
    # https://stackoverflow.com/questions/54678337/how-does-one-ignore-extra-arguments-passed-to-a-dataclass
    @classmethod
    def from_dict(cls, dict):    # "cls" is like "self" but for a @classmethod
        dataclass_fields = inspect.signature(cls).parameters  # an OrderedDict of the class attr keys
        return cls(**{  ## return a instantation of the class with the dict keypairs as parameters
            k: v for k, v in dict.items()   # items() returns the dict in a list of tuples
            if k in dataclass_fields  # checks if key is one of the class's parameters
        })
    
    def __post_init__(self):
        if self.start_time:          
            if self.timezone:
                self.start_time_iso = datetime.fromtimestamp(self.start_time, tz=ZoneInfo(self.timezone)).isoformat()
            else:
                self.start_time_iso = datetime.fromtimestamp(
                    self.start_time, tz=EASTERN_TIME).isoformat()
        if self.end_time:          
            if self.timezone:
                self.end_time_iso = datetime.fromtimestamp(self.end_time, tz=ZoneInfo(self.timezone)).isoformat()
            else:
                self.end_time_iso = datetime.fromtimestamp(
                    self.end_time, tz=EASTERN_TIME).isoformat()   
                
    # Added "dropna(axis='columns')" to drop empty columns and avoid FUTUREWARNING: 
    #       "FutureWarning: The behavior of DataFrame concatenation with empty 
    #       or all-NA entries is deprecated. In a future version, this will no longer
    #       exclude empty or all-NA columns when determining the result dtypes. To retain 
    #       the old behavior, exclude the relevant entries before the concat operation."
    def create_dataframe(self):
        return pd.DataFrame([self]).dropna(axis='columns', how='all')   #.set_index('id')
    
    
@dataclass
class PelotonRideGroup:
    rides: List[PelotonRide]
    
    def __str__(self):
        string = ""
        for ride in self.rides:
            string = string + "\n" + "\n" + ride.__repr__()
        return f"{self.__class__.__name__} ({len(self.rides)} rides):{string}"
    
    def create_dataframe(self):
        rides_list = [ride.create_dataframe() for ride in reversed(self.rides)]
        
        return pd.concat(rides_list, ignore_index=True)  # if set_index('id') above, set ignore_index=False 


################# FUNCTIONS ########################
# SQL database functions
def create_mariadb_engine(database: str) -> db.Engine:
    mariadb_url = db.URL.create(
        drivername="mysql+pymysql",
        username=MARIADB_USER,
        password=MARIADB_PASS,
        host=MARIADB_SERVER,
        database=database,
    )
    return db.create_engine(mariadb_url)


# def select_all_from_table(engine: db.Engine, table: str, index_col: str = None, 
#                           parse_dates: list[str] = None) -> pd.DataFrame:
#     with engine.connect() as conn:
#         df = pd.read_sql(
#             f"SELECT * from {table}",
#             conn,
#             index_col=index_col,
#             parse_dates=parse_dates
#             )
#     return df


# def get_peloton_data_from_sql(engine: db.Engine) -> pd.DataFrame:
#     with engine.connect() as conn:
#         df = pd.read_sql(
#             "SELECT * from peloton",
#             conn,
#             index_col='start_time_iso',
#             parse_dates=['start_time_iso', 'start_time_local']
#             )
#     return df


def export_peloton_data_to_sql(input_df: pd.DataFrame, engine: db.Engine, table: str, index: bool = False):
     with engine.connect() as conn:
        input_df.to_sql(table, conn, if_exists="append", index=False)
        

# Calculate number of new workouts not yet in DB
def calculate_new_workouts_num(py_conn: pylotoncycle.PylotonCycle, df_input: pd.DataFrame) -> int:
    total_workouts = py_conn.GetMe()["total_workouts"]
    existing_workouts = df_input.shape[0]
    new_workouts = total_workouts - existing_workouts

    print(f"Total Workouts: {total_workouts}")
    print(f"Workouts in Database: {existing_workouts}")
    print(f"New Workouts to Write: {new_workouts}")
    
    return new_workouts


def process_workouts(py_conn: pylotoncycle.PylotonCycle, workouts_num: int = None) -> pd.DataFrame:
    ride_group_list = []
    
    workouts = py_conn.GetRecentWorkouts(workouts_num)  ## defaults to all workouts if nothing passed

    for w in workouts:
        df_workout = pd.json_normalize(w)
        df_workout_ride = pd.json_normalize(w['ride'])
        workout_id = df_workout['id'].loc[0]
        ride_attributes_dict = {}
        
        # Loop through the regular columns in df_workout and then the "ride" columns
        ride_attributes_dict.update({column: df_workout[column][0] for column in df_workout.columns})
        ride_attributes_dict.update({f"ride_{column}": df_workout_ride[column][0] for column in df_workout_ride.columns})

        # Pull metrics from Peloton, copy into a dictionary, create DataFrames
        workout_metrics_by_id_dict = py_conn.GetWorkoutMetricsById(workout_id)
        
        # Loop through summaries (total_output, distance, calories)
        df_summaries = pd.json_normalize(workout_metrics_by_id_dict['summaries'])
        ride_attributes_dict.update({ df_summaries['slug'][index]: df_summaries['value'][index] for index, row in df_summaries.iterrows() })
                     
        # Loop through average & max values (output, cadence, resistance, speed, HR)
        df_metrics = pd.json_normalize(workout_metrics_by_id_dict['metrics'])
        df_average_values = df_metrics.set_index('slug')['average_value']
        df_max_values = df_metrics.set_index('slug')['max_value']
        ride_attributes_dict.update({ f"{index}_avg": value for index, value in df_average_values.items() })
        ride_attributes_dict.update({ f"{index}_max": value for index, value in df_max_values.items() })

        # Set "Strive Score" attribute & loop through HR Zone Duration columns        
        if 'effort_zones' in workout_metrics_by_id_dict.keys():
            df_effort_zones = pd.json_normalize(workout_metrics_by_id_dict['effort_zones'])
            df_hr_zone_durations = pd.json_normalize(workout_metrics_by_id_dict['effort_zones']['heart_rate_zone_durations'])

            ride_attributes_dict.update({ "strive_score": df_effort_zones['total_effort_points'][0] })
            ride_attributes_dict.update({ column: df_hr_zone_durations[column][0] for column in df_hr_zone_durations.columns })        

        # Create the PelotonRide object from the "ride_attributes_dict" dictionary you just created
        ride_object = PelotonRide.from_dict(ride_attributes_dict)

        # Add newly created ride object to the running list (which will be used after the loop to make a PelotonRideGroup object)
        ride_group_list.append(ride_object)
        print(f"Pulled and processed {ride_object.start_time_iso}")
                                 
    # After the loop, create a PelotonRideGroup object from the list of PelotonRide objects
    ride_group = PelotonRideGroup(ride_group_list)
    
    # Return a DataFrame of the Peloton rides using the create_dataframe() method in the PelotonRideGroup object
    return ride_group.create_dataframe()


def main():
    SQL_DB = "peloton"
    SQL_TABLE = "test"
    EXCEL_FILE = "/mnt/home-ds920/peloton_workouts.xlsx"

    py_conn = pylotoncycle.PylotonCycle(PELOTON_USERNAME, PELOTON_PASSWORD) 
        
    sql_engine = create_mariadb_engine(SQL_DB)
         
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
    

    df = process_workouts(py_conn, workouts_num=20)  ## might need to pull data in batches to avoid API timeout
    print(df)    
    df.to_csv(f"/mnt/home-ds920/asdf-{datetime.now().strftime('%Y-%m-%d %H-%M-%s')}.csv")
    
    export_peloton_data_to_sql(df, sql_engine, "test")
    
    
    
    ########## consider creating multiple SQL tables for stuff like 
    ##########  splits data, and joining them together!!!
    
    '''
    ideas for further improvement:
    
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
    
    
    
    ########## DON'T UNCOMMENT BELOW UNTIL YOU MAKE NEW TABLE ############
    ######################################################################
    # sql_engine = create_mariadb_engine(database="peloton")  # previous database was "zmv"
    # mariadb_df = get_peloton_data_from_sql(sql_engine)
    
  
    
        
        
if __name__ == "__main__":
    main()
    


################################################################################
################################################################################
###################### COMMENT JUNKYARD STARTS HERE ############################
################################################################################
################################################################################

    
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