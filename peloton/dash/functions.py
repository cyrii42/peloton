import pandas as pd
import sqlalchemy as db

from peloton.constants import EASTERN_TIME


def create_table_df(sql_engine: db.Engine) -> pd.DataFrame:
    with sql_engine.connect() as conn:
        df = pd.read_sql_table("peloton", conn)

    df['start_time_iso'] = pd.to_datetime(df['start_time_iso'], utc=True) 
    df_dti_naive = pd.DatetimeIndex(df['start_time_iso']).tz_localize(tz=None)   
    df_dti_aware = pd.DatetimeIndex(df['start_time_iso']).tz_convert(tz=EASTERN_TIME)

    # Add additional metrics
    df['min'] = [round((x / 60),0) for x in df['ride_duration'].tolist() if x != 0]
    df['length_min'] = [round((x / 60),0) for x in df['ride_length'].tolist()]
    df['output/min'] = [round((x[0] / (x[1] / 60)),2) 
                        for x in zip(df['total_output'].tolist(), df['ride_duration'].tolist()) 
                        if x[1] != 0]
    df['start_time'] = [x.strftime('%a %-m/%-d/%y %-I:%M %p') for x in df_dti_aware.tolist()]

    df['annual_periods'] = [x.to_period(freq='Y') for x in df_dti_naive]
    df['monthly_periods'] = [x.to_period(freq='M') for x in df_dti_naive]
    df['month'] = [x.strftime('%B %Y') for x in df_dti_aware]

    df = df.rename(columns={
        'total_output': 'output',
        'ride_title': 'title',
        'instructor_name': 'instructor',
    })

    # Change the column order
    # df = df.reindex(columns=['year', 'rides', 'days', 'calories', 'distance', 'difficulty', 'output/min'])

    return df