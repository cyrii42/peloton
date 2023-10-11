import pandas as pd
import sqlalchemy as db

from peloton.helpers import create_mariadb_engine


def get_sql_data_for_pivots(engine: db.Engine) -> pd.DataFrame():
    with engine.connect() as conn:
        df = pd.read_sql_table("peloton", conn)

    df['start_time_iso'] = pd.to_datetime(df['start_time_iso'], utc=True)    
    df_dti = pd.DatetimeIndex(df['start_time_iso']).tz_localize(tz=None)

    df['annual_periods'] = [x.to_period(freq='Y') for x in df_dti]
    df['monthly_periods'] = [x.to_period(freq='M') for x in df_dti]
    df['month'] = [x.month_name() + " " + str(x.year) for x in df_dti]
    df['year'] = [x.year for x in df_dti]
    # df['weekly_periods'] = [x.to_period(freq='W') for x in df_dti]

    output_list = df['total_output'].tolist()
    duration_list = df['ride_duration'].tolist()
    df['output_per_min'] = [(x[0] / (x[1] / 60)) for x in zip(output_list, duration_list) if x[1] != 0]
    df['duration_hrs'] = [round((x / 3600), 2) for x in duration_list if x != 0]
    df['unique_days'] = [x.date() for x in df['start_time_iso'].tolist()]

    df = df.rename(columns={
        'ride_title': 'title',
        'duration_hrs': 'hours', 
        'unique_days': 'days',
        'ride_difficulty_estimate': 'difficulty',
        'output_per_min': 'output/min',
        })
    
    return df.reset_index()


def get_pivot_table_year(df: pd.DataFrame, ascending: bool = True) -> pd.DataFrame():
    year_table = df.pivot_table(
        values=[
            'title', 
            'days',
            'hours',
            'calories',
            'distance',
            'difficulty',
            'output/min'
            ], 
        index=['annual_periods', 'year'],
        aggfunc= {
            'title': 'count', 
            'days': pd.Series.nunique, 
            'hours': 'sum', 
            'calories': 'mean', 
            'distance': 'sum', 
            'difficulty': 'mean', 
            'output/min': 'mean'
            }
        )

    year_table = year_table.sort_values(by=['annual_periods'], ascending=ascending)
    year_table = year_table.reset_index().drop(columns=['annual_periods']).round(2)
    year_table = year_table.rename(columns={
        'title': 'rides',
        'calories': 'avg_calories',
        'difficulty': 'avg_difficulty',
        'hours': 'total_hours',
        'distance': 'total_distance',
    })
    # Change the column order
    year_table = year_table.reindex(columns=['year', 'rides', 'days', 'total_hours', 'total_distance', 'avg_calories', 'avg_difficulty', 'output/min'])
    
    return year_table


def get_pivot_table_month(df: pd.DataFrame, ascending: bool = True) -> pd.DataFrame():
    month_table = df.pivot_table( 
        values=[
            'title', 
            'days',
            'hours',
            'calories',
            'distance',
            'difficulty',
            'output/min'
            ], 
        index=[
            'annual_periods', 
            'monthly_periods', 
            'month'
            ], 
        aggfunc= {
            'title': 'count', 
            'days': pd.Series.nunique, 
            'hours': 'sum', 
            'calories': 'mean', 
            'distance': 'sum', 
            'difficulty': 'mean', 
            'output/min': 'mean'
            }
        )

    month_table = month_table.sort_values(by=['monthly_periods'], ascending=ascending)
    month_table = month_table.reset_index().drop(columns=['annual_periods', 'monthly_periods']).round(2)
    month_table = month_table.rename(columns={
        'title': 'rides',
        'calories': 'avg_calories',
        'difficulty': 'avg_difficulty',
        'hours': 'total_hours',
        'distance': 'total_distance',
    })
    # Change the column order
    month_table = month_table.reindex(columns=['month', 'rides', 'days', 'total_hours', 'total_distance', 'avg_calories', 'avg_difficulty', 'output/min'])
    
    return month_table


def main():
    mariadb_engine = create_mariadb_engine(database="peloton")
    
    df = get_sql_data_for_pivots(mariadb_engine)
    
    year_table = get_pivot_table_year(df)
    month_table = get_pivot_table_month(df)
    
    ##### Aug 31, 2023: added "to_string()" at the end so that full table prints #####
    # print(year_table[['title', 'unique_days', 'duration_min', 'distance', 'calories', 'difficulty', 'output_per_min']].round(2).to_string())  
    # print(month_table[['title', 'unique_days', 'duration_min', 'distance', 'calories', 'difficulty', 'output_per_min']].round(2).to_string())  

    print(year_table)
    print(month_table)

    # print(df['monthly_periods'].nunique())

    # table.to_excel('test2.xlsx', sheet_name='peloton_pivot', index=True, float_format='%.2f')


if __name__ == "__main__":
    main()

