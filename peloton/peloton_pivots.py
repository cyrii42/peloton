import pandas as pd
import sqlalchemy as db

from peloton.helpers import create_mariadb_engine


def get_sql_data_for_pivots(engine: db.Engine) -> pd.DataFrame():
    with engine.connect() as conn:
        df = pd.read_sql_table("peloton", conn)

    df['start_time_iso'] = pd.to_datetime(df['start_time_iso'], utc=True)    

    df['annual_periods'] = [x.to_period(freq='Y') for x in df['start_time_iso'].tolist()]
    df['monthly_periods'] = [x.to_period(freq='M') for x in df['start_time_iso'].tolist()]
    df['month_name'] = [x.month_name() + " " + str(x.year) for x in df['start_time_iso'].tolist()]
    # df['weekly_periods'] = [x.to_period(freq='W') for x in df['start_time_iso'].tolist()]

    output_list = df['total_output'].tolist()
    duration_list = df['ride_duration'].tolist()
    df['output_per_min'] = [(x[0] / (x[1] / 60)) for x in zip(output_list, duration_list) if x[1] != 0]
    df['duration_min'] = [int(round((x / 60), 0)) for x in duration_list if x != 0]
    df['unique_days'] = [x.date() for x in df['start_time_iso'].tolist()]
    
    return df.reset_index()

def get_pivot_table_year(df: pd.DataFrame) -> pd.DataFrame():
    year_table = df.pivot_table(
        values=[
            'ride_title', 
            'unique_days',
            'duration_min',
            'calories',
            'distance',
            'ride_difficulty_estimate',
            'output_per_min'
            ], 
        index=['annual_periods'],
        aggfunc= {
            'ride_title': 'count', 
            'unique_days': pd.Series.nunique, 
            'duration_min': 'sum', 
            'calories': 'mean', 
            'distance': 'sum', 
            'ride_difficulty_estimate': 'mean', 
            'output_per_min': 'mean'
            }
        )
    
    return year_table.reset_index().round(2)

def get_pivot_table_month(df: pd.DataFrame) -> pd.DataFrame():
    month_table = df.pivot_table( 
        values=[
            'ride_title', 
            'unique_days',
            'duration_min',
            'calories',
            'distance',
            'ride_difficulty_estimate',
            'output_per_min'
            ], 
        index=[
            'annual_periods', 
            'monthly_periods', 
            'month_name'
            ], 
        aggfunc= {
            'ride_title': 'count', 
            'unique_days': pd.Series.nunique, 
            'duration_min': 'sum', 
            'calories': 'mean', 
            'distance': 'sum', 
            'ride_difficulty_estimate': 'mean', 
            'output_per_min': 'mean'
            }
        )
    
    return month_table.reset_index().round(2)


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

