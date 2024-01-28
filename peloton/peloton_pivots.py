import pandas as pd

import peloton.constants as const
from peloton.peloton_processor import PelotonProcessor


class PelotonPivots():
    ''' Object for creating, printing, and saving pivot tables from Peloton data.'''
    
    def __init__(self, df_processed_workout_data: pd.DataFrame):
        self.df_processed_workout_data = df_processed_workout_data
        self.df_pivots = self.create_df_for_pivots()
        self.year_table = self.create_year_table()
        self.month_table = self.create_month_table()
        self.totals_table = self.create_totals_table()

    def create_df_for_pivots(self) -> pd.DataFrame:
        df = self.df_processed_workout_data
        
        df['start_time_iso'] = pd.to_datetime(df['start_time_iso'], utc=True)
        df_dti = pd.DatetimeIndex(df['start_time_iso']).tz_convert(tz=None)
        df_dti_localized = pd.DatetimeIndex(df['start_time_iso']).tz_convert(tz=const.EASTERN_TIME)

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
        
        return df.reset_index()

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

    def print_pivot_tables(self) -> None:
        print("")
        print("                             GRAND TOTALS")
        print(self.totals_table)
        print("")
        print(self.year_table)
        print("")
        print(self.month_table)

    def write_csv_files(self) -> None:
        self.year_table.to_csv(f"{const.PELOTON_CSV_DIR}/year_table.csv")
        self.month_table.to_csv(f"{const.PELOTON_CSV_DIR}/month_table.csv")
        self.totals_table.to_csv(f"{const.PELOTON_CSV_DIR}/totals_table.csv")
        self.df_processed_workout_data.to_csv(f"{const.PELOTON_CSV_DIR}/all_data.csv")
   

def main():
    print("This is a module, not a script.")





if __name__ == "__main__":
    main()