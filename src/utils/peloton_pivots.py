import pandas as pd
import sqlalchemy as db
from utils.helpers import create_mariadb_engine

def get_sql_data_for_pivots(engine: db.Engine) -> pd.DataFrame():
    with engine.connect() as conn:
       df = pd.read_sql("SELECT * from peloton", conn, parse_dates=['start_time_iso', 'start_time_local'])

    df['annual_periods'] = [x.to_period(freq='Y') for x in df['start_time_iso'].tolist()]
    df['monthly_periods'] = [x.to_period(freq='M') for x in df['start_time_iso'].tolist()]
    df['month_name'] = [x.month_name() + " " + str(x.year) for x in df['start_time_iso'].tolist()]
    # df['weekly_periods'] = [x.to_period(freq='W') for x in df['start_time_iso'].tolist()]

    output_list = df['output'].tolist()
    duration_list = df['duration'].tolist()
    df['output_per_min'] = [(x[0] / (x[1] / 60)) for x in zip(output_list, duration_list)]
    df['duration_min'] = [int(round((x / 60),0)) for x in duration_list]
    df['unique_days'] = [x.date() for x in df['start_time_local'].tolist()]
    
    return df.reset_index()

def get_pivot_table_year(df: pd.DataFrame) -> pd.DataFrame():
    year_table = df.pivot_table(
        values=[
            'title', 
            'unique_days',
            'duration_min',
            'calories',
            'distance',
            'difficulty',
            'output_per_min'
            ], 
        index=['annual_periods'],
        aggfunc= {
            'title': 'count', 
            'unique_days': pd.Series.nunique, 
            'duration_min': 'sum', 
            'calories': 'mean', 
            'distance': 'sum', 
            'difficulty': 'mean', 
            'output_per_min': 'mean'
            }
        )
    
    return year_table.reset_index().round(2)

def get_pivot_table_month(df: pd.DataFrame) -> pd.DataFrame():
    month_table = df.pivot_table( 
        values=[
            'title', 
            'unique_days',
            'duration_min',
            'calories',
            'distance',
            'difficulty',
            'output_per_min'
            ], 
        index=[
            'annual_periods', 
            'monthly_periods', 
            'month_name'
            ], 
        aggfunc= {
            'title': 'count', 
            'unique_days': pd.Series.nunique, 
            'duration_min': 'sum', 
            'calories': 'mean', 
            'distance': 'sum', 
            'difficulty': 'mean', 
            'output_per_min': 'mean'
            }
        )
    
    return month_table.reset_index().round(2)


def main():
    mariadb_engine = create_mariadb_engine(database="zmv")
    
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

