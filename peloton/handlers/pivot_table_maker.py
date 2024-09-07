import pandas as pd
from peloton.constants import EASTERN_TIME


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
        df = df.copy()     
        df_dti_localized = pd.DatetimeIndex(df['start_time']).tz_convert(tz=EASTERN_TIME)
        df_dti = df_dti_localized.tz_localize(tz=None)

        df['annual_periods'] = [x.to_period(freq='Y') for x in df_dti]
        df['monthly_periods'] = [x.to_period(freq='M') for x in df_dti]
        df['weekly_periods'] = [x.to_period(freq='W') for x in df_dti]
        df['month'] = [x.month_name() + " " + str(x.year) for x in df_dti_localized]
        df['year'] = [x.year for x in df_dti_localized]
        df['days'] = [x.day for x in df_dti_localized]
        df['date'] = [f"{str(x.year)}-{str(x.month)}-{str(x.day)}" for x in df_dti_localized]

        df = df.rename(columns={
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


def main():
    print("This is a module, not a script.")


if __name__ == "__main__":
    main()