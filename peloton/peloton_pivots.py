import pandas as pd
import sqlalchemy as db

from peloton.constants import EASTERN_TIME
from peloton.helpers import create_mariadb_engine


def get_sql_data_for_pivots(engine: db.Engine) -> pd.DataFrame:
    """ Fetches Peloton workout data from SQL server and performs 
    transformations necessary to generate pivot tables. """
    
    with engine.connect() as conn:
        df = pd.read_sql_table("peloton", conn)

    df['start_time_iso'] = pd.to_datetime(df['start_time_iso'], utc=True)
    df_dti = pd.DatetimeIndex(df['start_time_iso']).tz_convert(tz=None)
    df_dti_localized = pd.DatetimeIndex(df['start_time_iso']).tz_convert(tz=EASTERN_TIME)

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


def get_pivot_table_year(df: pd.DataFrame, ascending: bool = True) -> pd.DataFrame:
    """ Generates a year-by-year pivot table from Peloton data """
    
    year_table = df.pivot_table(
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


def get_grand_totals_table(year_table: pd.DataFrame) -> pd.DataFrame:
    """Takes an annual pivot table and returns a DataFrame with the grand totals (or averages)"""
  
    sum_cols = year_table[['rides', 'total_hours', 'total_miles']].sum()
    avg_cols = year_table[['avg_calories', 'avg_output/min']].mean().round(2)

    col_list = ['rides', 'total_hours', 'total_miles', 'avg_calories', 'avg_output/min']
    dtypes_dict = {col: ('int64' if col == 'rides' else 'float64') for col in col_list}

    totals_table = pd.concat([sum_cols, avg_cols]).to_frame().transpose().astype(dtypes_dict)
    
    return totals_table


def get_pivot_table_month(df: pd.DataFrame, ascending: bool = True) -> pd.DataFrame:
    """ Generates a month-by-month pivot table from Peloton data """
    
    month_table = df.pivot_table( 
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
   

def main():
    mariadb_engine = create_mariadb_engine(database="peloton")
    
    df = get_sql_data_for_pivots(mariadb_engine)
    
    year_table = get_pivot_table_year(df)
    month_table = get_pivot_table_month(df)
    totals_table = get_grand_totals_table(year_table) 

    print("                             GRAND TOTALS")
    print(totals_table)
    print("")
    print(year_table)
    print("")
    print(month_table)




if __name__ == "__main__":
    main()





    

# def get_sql_data_for_pivots(sql_engine: db.Engine) -> pd.DataFrame:
#     """ Fetches Peloton workout data from SQL server and performs 
#     transformations necessary to generate pivot tables. """
    
#     with sql_engine.connect() as conn:
#         df = pd.read_sql_table("peloton", conn)

#     df['start_time_iso'] = pd.to_datetime(df['start_time_iso'], utc=True)
#     df_dti = pd.DatetimeIndex(df['start_time_iso']).tz_convert(tz=None)
#     df_dti_localized = pd.DatetimeIndex(df['start_time_iso']).tz_convert(tz=EASTERN_TIME)

#     df['annual_periods'] = [x.to_period(freq='Y') for x in df_dti]
#     df['monthly_periods'] = [x.to_period(freq='M') for x in df_dti]
#     df['weekly_periods'] = [x.to_period(freq='W') for x in df_dti]
#     df['month'] = [x.month_name() + " " + str(x.year) for x in df_dti_localized]
#     df['year'] = [x.year for x in df_dti_localized]
#     df['days'] = [x.day for x in df_dti_localized]
#     df['date'] = [f"{str(x.year)}-{str(x.month)}-{str(x.day)}" for x in df_dti_localized]

#     output_list = df['total_output'].tolist()
#     duration_list = df['ride_duration'].tolist()
#     df['output_per_min'] = [(x[0] / (x[1] / 60)) for x in zip(output_list, duration_list) if x[1] != 0]
#     df['duration_hrs'] = [round((x / 3600), 2) for x in duration_list if x != 0]

#     df = df.rename(columns={
#         'ride_title': 'title',
#         'duration_hrs': 'hours', 
#         'output_per_min': 'output/min',
#         })
    
#     return df.reset_index()


# def get_pivot_table_year(df: pd.DataFrame, ascending: bool = True) -> pd.DataFrame:
#     """ Generates a year-by-year pivot table from Peloton data """
    
#     year_table = df.pivot_table(
#         values=[
#             'title', 
#             'date',
#             'hours',
#             'calories',
#             'distance',
#             'output/min',
#             ], 
#         index=['annual_periods', 'year'],
#         aggfunc= {
#             'title': 'count', 
#             'date': pd.Series.nunique, 
#             'hours': 'sum', 
#             'calories': 'mean', 
#             'distance': 'sum', 
#             'output/min': 'mean',
#             }
#         )

#     year_table = year_table.sort_values(by=['annual_periods'], ascending=ascending)
#     year_table = year_table.reset_index().drop(columns=['annual_periods']).round(2)
#     year_table = year_table.rename(columns={
#         'date': 'days',
#         'title': 'rides',
#         'calories': 'avg_calories',
#         'hours': 'total_hours',
#         'distance': 'total_miles',
#         'output/min': "avg_output/min",
#     })
#     # Change the column order
#     year_table = year_table.reindex(columns=['year', 'rides', 'days', 'total_hours', 
#                                              'total_miles', 'avg_calories', 'avg_output/min'])
    
#     return year_table


# def get_grand_totals_table(year_table: pd.DataFrame) -> pd.DataFrame:
#     """Takes an annual pivot table and returns a DataFrame with the grand totals (or averages)"""
  
#     sum_cols = year_table[['rides', 'total_hours', 'total_miles']].sum()
#     avg_cols = year_table[['avg_calories', 'avg_output/min']].mean().round(2)

#     col_list = ['rides', 'total_hours', 'total_miles', 'avg_calories', 'avg_output/min']
#     dtypes_dict = {col: ('int64' if col == 'rides' else 'float64') for col in col_list}

#     totals_table = pd.concat([sum_cols, avg_cols]).to_frame().transpose().astype(dtypes_dict)
    
#     return totals_table


# def get_pivot_table_month(df: pd.DataFrame, ascending: bool = True) -> pd.DataFrame:
#     """ Generates a month-by-month pivot table from Peloton data """
    
#     month_table = df.pivot_table( 
#         values=[
#             'title', 
#             'date',
#             'hours',
#             'calories',
#             'distance',
#             'output/min',
#             ], 
#         index=[
#             'annual_periods', 
#             'monthly_periods', 
#             'month',
#             ], 
#         aggfunc= {
#             'title': 'count', 
#             'date': pd.Series.nunique, 
#             'hours': 'sum', 
#             'calories': 'mean', 
#             'distance': 'sum', 
#             'output/min': 'mean',
#             }
#         )

#     month_table = month_table.sort_values(by=['monthly_periods'], ascending=ascending)
#     month_table = month_table.reset_index().drop(columns=['annual_periods', 'monthly_periods']).round(2)
#     month_table = month_table.rename(columns={
#         'date': 'days',
#         'title': 'rides',
#         'calories': 'avg_calories',
#         'hours': 'total_hours',
#         'distance': 'total_miles',
#         'output/min': "avg_output/min",
#     })
#     # Change the column order
#     month_table = month_table.reindex(columns=['month', 'rides', 'days', 'total_hours', 
#                                                'total_miles', 'avg_calories', 'avg_output/min'])
    
#     return month_table