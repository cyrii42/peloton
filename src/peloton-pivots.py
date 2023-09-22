import pandas as pd
from config.config import mariadb_engine

with mariadb_engine.connect() as conn:
    df = pd.read_sql("SELECT * from peloton", conn, parse_dates=['start_time_iso', 'start_time_local'])

df['annual_periods'] = [x.to_period(freq='Y') for x in df['start_time_iso'].tolist()]
df['monthly_periods'] = [x.to_period(freq='M') for x in df['start_time_iso'].tolist()]
df['month_name'] = [x.month_name() for x in df['start_time_iso'].tolist()]
# df['weekly_periods'] = [x.to_period(freq='W') for x in df['start_time_iso'].tolist()]

output_list = df['output'].tolist()
duration_list = df['duration'].tolist()
df['output_per_min'] = [(x[0] / (x[1] / 60)) for x in zip(output_list, duration_list)]
df['duration_min'] = [int(round((x / 60),0)) for x in duration_list]
df['unique_days'] = [x.date() for x in df['start_time_local'].tolist()]

month_table = pd.pivot_table(df, 
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

year_table = pd.pivot_table(df, 
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

##### Aug 31, 2023: added "to_string()" at the end so that full table prints #####
print(year_table[['title', 'unique_days', 'duration_min', 'distance', 'calories', 'difficulty', 'output_per_min']].round(2).to_string())  
print(month_table[['title', 'unique_days', 'duration_min', 'distance', 'calories', 'difficulty', 'output_per_min']].round(2).to_string())  

# print(df['monthly_periods'].nunique())

# table.to_excel('test2.xlsx', sheet_name='peloton_pivot', index=True, float_format='%.2f')
