from zoneinfo import ZoneInfo

import pandas as pd

'''
METHODS
create_processed_table_for_stout
create_df_for_pivots
create_year_table
create_month_table
create_totals_table
print_pivot_tables
write_csv_files
write_to_google_sheet

INSTANCE VARIABLES
peloton_processor (from __init__())
df_processed_workout_data (from __init__())
df_raw_workouts_data (from __init__())
df_raw_metrics_data (from __init__())
df_pivots (from __init__())
year_table (from __init__())
month_table (from __init__())
totals_table (from __init__())
processed_table (from __init__())
spread = None (from __init__())
'''


class PelotonPivots():
    ''' Object for creating, printing, and saving pivot tables from Peloton data.'''
    
    def __init__(self, df_processed: pd.DataFrame):
        self.df_pivots = self.create_df_for_pivots(df_processed)
        self.year_table = self.create_year_table()
        self.month_table = self.create_month_table()
        self.totals_table = self.create_totals_table()


    def regenerate_tables(self, new_df_processed: pd.DataFrame) -> None:
        self.df_pivots = self.create_df_for_pivots(new_df_processed)
        self.year_table = self.create_year_table()
        self.month_table = self.create_month_table()
        self.totals_table = self.create_totals_table()
        

    def create_df_for_pivots(self, df: pd.DataFrame) -> pd.DataFrame:       
        df['start_time_iso'] = pd.to_datetime(df['start_time_iso'], utc=True)
        df_dti = pd.DatetimeIndex(df['start_time_iso']).tz_convert(tz=None)
        df_dti_localized = pd.DatetimeIndex(df['start_time_iso']).tz_convert(tz=ZoneInfo("America/New_York"))

        df['annual_periods'] = [x.to_period(freq='Y') for x in df_dti]
        df['monthly_periods'] = [x.to_period(freq='M') for x in df_dti]
        df['weekly_periods'] = [x.to_period(freq='W') for x in df_dti]
        df['month'] = [x.month_name() + " " + str(x.year) for x in df_dti_localized]
        df['year'] = [x.year for x in df_dti_localized]
        df['days'] = [x.day for x in df_dti_localized]
        df['date'] = [f"{str(x.year)}-{str(x.month)}-{str(x.day)}" for x in df_dti_localized]

        output_list = df['total_output'].tolist()
        duration_list = df['ride_duration'].tolist()
        df['output_per_min'] = [(x[0] / (x[1] / 60)) for x in zip(output_list, duration_list) if x[1] != 0]
        df['duration_hrs'] = [round((x / 3600), 2) for x in duration_list if x != 0]

        df = df.rename(columns={
            'ride_title': 'title',
            'duration_hrs': 'hours', 
            'output_per_min': 'output/min',
            })
        
        return df.reset_index(drop=True)


    def create_year_table(self, ascending: bool = True) -> pd.DataFrame:
        """ Generates a year-by-year pivot table from Peloton data """
        
        year_table = self.df_pivots.pivot_table(
            values=[
                'title', 
                'date',
                'hours',
                'calories',
                'distance',
                'output/min',
                ], 
            index=['annual_periods', 'year'],
            aggfunc= {
                'title': 'count', 
                'date': pd.Series.nunique, 
                'hours': 'sum', 
                'calories': 'mean', 
                'distance': 'sum', 
                'output/min': 'mean',
                }
            )

        year_table = year_table.sort_values(by=['annual_periods'], ascending=ascending)
        year_table = year_table.reset_index().drop(columns=['annual_periods']).round(2)
        year_table = year_table.rename(columns={
            'date': 'days',
            'title': 'rides',
            'calories': 'avg_calories',
            'hours': 'total_hours',
            'distance': 'total_miles',
            'output/min': "avg_output/min",
        })
        # Change the column order
        year_table = year_table.reindex(columns=['year', 'rides', 'days', 'total_hours', 
                                                'total_miles', 'avg_calories', 'avg_output/min'])
        
        return year_table


    def create_month_table(self, ascending: bool = True) -> pd.DataFrame:
        """ Generates a month-by-month pivot table from Peloton data """
        
        month_table = self.df_pivots.pivot_table( 
            values=[
                'title', 
                'date',
                'hours',
                'calories',
                'distance',
                'output/min',
                ], 
            index=[
                'annual_periods', 
                'monthly_periods', 
                'month',
                ], 
            aggfunc= {
                'title': 'count', 
                'date': pd.Series.nunique, 
                'hours': 'sum', 
                'calories': 'mean', 
                'distance': 'sum', 
                'output/min': 'mean',
                }
            )

        month_table = month_table.sort_values(by=['monthly_periods'], ascending=ascending)
        month_table = month_table.reset_index().drop(columns=['annual_periods', 'monthly_periods']).round(2)
        month_table = month_table.rename(columns={
            'date': 'days',
            'title': 'rides',
            'calories': 'avg_calories',
            'hours': 'total_hours',
            'distance': 'total_miles',
            'output/min': "avg_output/min",
        })
        # Change the column order
        month_table = month_table.reindex(columns=['month', 'rides', 'days', 'total_hours', 
                                                'total_miles', 'avg_calories', 'avg_output/min'])
        
        return month_table


    def create_totals_table(self) -> pd.DataFrame:
        """Takes an annual pivot table and returns a DataFrame with the grand totals (or averages)"""
    
        sum_cols = self.year_table[['rides', 'total_hours', 'total_miles']].sum()
        avg_cols = self.year_table[['avg_calories', 'avg_output/min']].mean().round(2)

        col_list = ['rides', 'total_hours', 'total_miles', 'avg_calories', 'avg_output/min']
        dtypes_dict = {col: ('int64' if col == 'rides' else 'float64') for col in col_list}

        totals_table = pd.concat([sum_cols, avg_cols]).to_frame().transpose().astype(dtypes_dict)
        
        return totals_table


# class PelotonPivotsOld():
#     ''' Object for creating, printing, and saving pivot tables from Peloton data.'''
    
#     def __init__(self, peloton_processor: PelotonProcessor):
#         self.peloton_processor = peloton_processor
#         self.df_processed_workout_data = self.peloton_processor.ingest_processed_data_from_sql()
#         self.df_raw_workouts_data = self.peloton_processor.ingest_raw_workout_data_from_sql()
#         self.df_raw_metrics_data = self.peloton_processor.ingest_raw_metrics_data_from_sql()
#         self.df_pivots = self.create_df_for_pivots()
#         self.year_table = self.create_year_table()
#         self.month_table = self.create_month_table()
#         self.totals_table = self.create_totals_table()
#         self.processed_table = self.create_processed_table_for_stout()
#         self.spread = None

#     def create_processed_table_for_stout(self) -> pd.DataFrame:
#         df = self.peloton_processor.df_processed
#         df['start_time_strf'] = [datetime.fromisoformat(x).strftime('%a %h %d %I:%M %p') 
#                                                                 for x in df['start_time_iso'].tolist()]
#         return df[['start_time_strf', 'ride_title', 'instructor_name', 'total_output', 
#                                                 'distance', 'calories', 'heart_rate_avg', 'strive_score']]

#     def create_df_for_pivots(self) -> pd.DataFrame:
#         df = self.df_processed_workout_data
        
#         df['start_time_iso'] = pd.to_datetime(df['start_time_iso'], utc=True) # .apply(lambda x: pd.Timestamp(x, tz='America/New_York'))????
#         df_dti = pd.DatetimeIndex(df['start_time_iso']).tz_convert(tz=None)
#         df_dti_localized = pd.DatetimeIndex(df['start_time_iso']).tz_convert(tz=EASTERN_TIME)

#         df['annual_periods'] = [x.to_period(freq='Y') for x in df_dti]
#         df['monthly_periods'] = [x.to_period(freq='M') for x in df_dti]
#         df['weekly_periods'] = [x.to_period(freq='W') for x in df_dti]
#         df['month'] = [x.month_name() + " " + str(x.year) for x in df_dti_localized]
#         df['year'] = [x.year for x in df_dti_localized]
#         df['days'] = [x.day for x in df_dti_localized]
#         df['date'] = [f"{str(x.year)}-{str(x.month)}-{str(x.day)}" for x in df_dti_localized]

#         output_list = df['total_output'].tolist()
#         duration_list = df['ride_duration'].tolist()
#         df['output_per_min'] = [(x[0] / (x[1] / 60)) for x in zip(output_list, duration_list) if x[1] != 0]
#         df['duration_hrs'] = [round((x / 3600), 2) for x in duration_list if x != 0]

#         df = df.rename(columns={
#             'ride_title': 'title',
#             'duration_hrs': 'hours', 
#             'output_per_min': 'output/min',
#             })
        
#         return df.reset_index(drop=True)

#     def create_year_table(self, ascending: bool = True) -> pd.DataFrame:
#         """ Generates a year-by-year pivot table from Peloton data """
        
#         year_table = self.df_pivots.pivot_table(
#             values=[
#                 'title', 
#                 'date',
#                 'hours',
#                 'calories',
#                 'distance',
#                 'output/min',
#                 ], 
#             index=['annual_periods', 'year'],
#             aggfunc= {
#                 'title': 'count', 
#                 'date': pd.Series.nunique, 
#                 'hours': 'sum', 
#                 'calories': 'mean', 
#                 'distance': 'sum', 
#                 'output/min': 'mean',
#                 }
#             )

#         year_table = year_table.sort_values(by=['annual_periods'], ascending=ascending)
#         year_table = year_table.reset_index().drop(columns=['annual_periods']).round(2)
#         year_table = year_table.rename(columns={
#             'date': 'days',
#             'title': 'rides',
#             'calories': 'avg_calories',
#             'hours': 'total_hours',
#             'distance': 'total_miles',
#             'output/min': "avg_output/min",
#         })
#         # Change the column order
#         year_table = year_table.reindex(columns=['year', 'rides', 'days', 'total_hours', 
#                                                 'total_miles', 'avg_calories', 'avg_output/min'])
        
#         return year_table


#     def create_month_table(self, ascending: bool = True) -> pd.DataFrame:
#         """ Generates a month-by-month pivot table from Peloton data """
        
#         month_table = self.df_pivots.pivot_table( 
#             values=[
#                 'title', 
#                 'date',
#                 'hours',
#                 'calories',
#                 'distance',
#                 'output/min',
#                 ], 
#             index=[
#                 'annual_periods', 
#                 'monthly_periods', 
#                 'month',
#                 ], 
#             aggfunc= {
#                 'title': 'count', 
#                 'date': pd.Series.nunique, 
#                 'hours': 'sum', 
#                 'calories': 'mean', 
#                 'distance': 'sum', 
#                 'output/min': 'mean',
#                 }
#             )

#         month_table = month_table.sort_values(by=['monthly_periods'], ascending=ascending)
#         month_table = month_table.reset_index().drop(columns=['annual_periods', 'monthly_periods']).round(2)
#         month_table = month_table.rename(columns={
#             'date': 'days',
#             'title': 'rides',
#             'calories': 'avg_calories',
#             'hours': 'total_hours',
#             'distance': 'total_miles',
#             'output/min': "avg_output/min",
#         })
#         # Change the column order
#         month_table = month_table.reindex(columns=['month', 'rides', 'days', 'total_hours', 
#                                                 'total_miles', 'avg_calories', 'avg_output/min'])
        
#         return month_table

#     def create_totals_table(self) -> pd.DataFrame:
#         """Takes an annual pivot table and returns a DataFrame with the grand totals (or averages)"""
    
#         sum_cols = self.year_table[['rides', 'total_hours', 'total_miles']].sum()
#         avg_cols = self.year_table[['avg_calories', 'avg_output/min']].mean().round(2)

#         col_list = ['rides', 'total_hours', 'total_miles', 'avg_calories', 'avg_output/min']
#         dtypes_dict = {col: ('int64' if col == 'rides' else 'float64') for col in col_list}

#         totals_table = pd.concat([sum_cols, avg_cols]).to_frame().transpose().astype(dtypes_dict)
        
#         return totals_table

#     def print_pivot_tables(self) -> None:
#         print("")
#         print("                             GRAND TOTALS")
#         print(self.totals_table)
#         print("")
#         print(self.year_table)
#         print("")
#         print(self.month_table)

#     def write_csv_files(self) -> None:
#         self.year_table.to_csv(f"{PELOTON_CSV_DIR}/year_table.csv")
#         self.month_table.to_csv(f"{PELOTON_CSV_DIR}/month_table.csv")
#         self.totals_table.to_csv(f"{PELOTON_CSV_DIR}/totals_table.csv")
#         self.df_processed_workout_data.to_csv(f"{PELOTON_CSV_DIR}/processed_workouts_data.csv")
#         self.df_raw_workouts_data.to_csv(f"{PELOTON_CSV_DIR}/raw_workouts_data.csv")
#         self.df_raw_metrics_data.to_csv(f"{PELOTON_CSV_DIR}/raw_metrics_data.csv")

#     def write_to_google_sheet(self, spreadsheet_id: str = PELOTON_SPREADSHEET) -> None:
#         spread = Spread(spreadsheet_id)

#         worksheets = {
#             'Processed Data': self.df_processed_workout_data,
#             'Raw Metrics Data': self.df_raw_metrics_data,
#             'Raw Workouts Data': self.df_raw_workouts_data,
#             'Year Table': self.year_table,
#             'Month Table': self.month_table,
#             'Totals Table': self.totals_table
#         }

#         for sheet_name, sheet_df in worksheets.items():
#             last_existing_row = sheet_df.shape[0] + 1
#             starting_row = last_existing_row + 1

#             spread.df_to_sheet(sheet_df, 
#                                sheet=sheet_name, 
#                                replace=True, 
#                                index=False, 
#                                headers=True, 
#                                freeze_headers=True, 
#                                start=(1, 1))


def main():
    print("This is a module, not a script.")


if __name__ == "__main__":
    main()