import json
import sqlite3
import sqlalchemy as db
import pandas as pd
from pathlib import Path
from pprint import pprint
from sqlalchemy.dialects.sqlite import TEXT, INTEGER, FLOAT

from peloton import (DATA_DIR, SQLITE_FILENAME, PelotonJSONWriter,
                     PelotonProcessor, create_mariadb_engine, PelotonWorkoutData)

SQLITE_TEST_FILENAME = f"sqlite:///{DATA_DIR.joinpath('peloton_test.db').resolve()}"

sqlite_engine = db.create_engine(SQLITE_FILENAME)
metadata_obj = db.MetaData()

def main():
    # create_processed_df_table()
    pp = PelotonProcessor()

    # workout = pp.workouts[0]
    # print(pd.json_normalize(workout.model_dump()).columns)

    df = pd.concat([pd.json_normalize(workout.model_dump()).dropna(axis='columns', how='all') for workout in pp.workouts], ignore_index=True)
    print(df)
    
    # df = pp.processed_df
    print(df.info())
    # print(df['instructor_json'].dropna())

    with sqlite_engine.connect() as conn:
        df.to_sql("processed_df", conn, if_exists="append", index=False)  

def create_processed_df_table() -> db.Table:

    peloton_processed_df_table = db.Table(
        "processed_df",
        metadata_obj,
        db.Column('workout_id', TEXT, primary_key=True), 
        db.Column('start_time', TEXT, nullable=False), 
        db.Column('end_time', TEXT), 
        db.Column('metrics_type', TEXT), 
        db.Column('workout_type', TEXT),
        db.Column('leaderboard_rank', INTEGER), 
        db.Column('total_leaderboard_users', INTEGER),
        db.Column('average_effort_score', FLOAT),
        db.Column('leaderboard_percentile', FLOAT), 
        db.Column('title', TEXT), 
        db.Column('description', TEXT), 
        db.Column('ride_length', INTEGER),
        db.Column('ride_duration', INTEGER),  
        db.Column('image_url', TEXT), 
        db.Column('difficulty_estimate', FLOAT),
        db.Column('fitness_discipline', TEXT), 
        db.Column('ride_id', TEXT), 
        db.Column('avg_output', FLOAT), 
        db.Column('avg_cadence', FLOAT),
        db.Column('avg_resistance', FLOAT), 
        db.Column('avg_speed', FLOAT),
        db.Column('avg_heart_rate', FLOAT),
        db.Column('max_output', INTEGER),
        db.Column('max_cadence', INTEGER), 
        db.Column('max_resistance', INTEGER), 
        db.Column('max_speed', FLOAT), 
        db.Column('max_heart_rate', INTEGER),
        db.Column('total_output', INTEGER), 
        db.Column('distance', FLOAT), 
        db.Column('calories', INTEGER), 
        db.Column('hr_zone1', INTEGER), 
        db.Column('hr_zone2', INTEGER),
        db.Column('hr_zone3', INTEGER), 
        db.Column('hr_zone4', INTEGER), 
        db.Column('hr_zone5', INTEGER), 
        db.Column('effort_score', FLOAT), 
        db.Column('output_per_min', FLOAT),
        db.Column('duration_hrs', FLOAT), 
        db.Column('instructor_json', TEXT), 
        db.Column('instructor_name', TEXT), 
        db.Column('instructor_id', TEXT),
        db.Column('duration', FLOAT),
    )
    metadata_obj.create_all(sqlite_engine)

#     jw = PelotonJSONWriter()
#     all_workouts = jw.all_workouts

#     # workout_dicts = [make_workout_dict(workout) for workout in all_workouts]
    
#     peloton_table = create_table()
#     # metadata_obj.create_all(sqlite_engine)

#     stmt = db.insert(peloton_table).values(all_workouts[0].model_dump_json())
#     print(stmt)

    
    # # stmt = db.insert(peloton_table).values(
    # #     workout_id=workout.workout_id, 
    # #     summary_raw=json.dumps(workout.summary_raw),
    # #     metrics_raw=json.dumps(workout.metrics_raw),
    # #     summary=workout.summary.model_dump_json(),
    # #     metrics=workout.metrics.model_dump_json()
    # # )

    # with sqlite_engine.connect() as conn:
    #     conn.execute(
    #         db.insert(peloton_table),
    #         workout_dicts,
    #     )
    #     conn.commit()

def make_workout_dict(workout: PelotonWorkoutData) -> dict:
    return {
        "workout_id": workout.workout_id,
        "summary_raw": json.dumps(workout.summary_raw),
        "metrics_raw": json.dumps(workout.metrics_raw),
        "summary": workout.summary.model_dump_json(),
        "metrics": workout.metrics.model_dump_json(),
    }

def create_table():
    
    peloton_table = db.Table(
        "peloton_json",
        metadata_obj,
        db.Column("workout_id", TEXT, primary_key=True),
        db.Column("summary_raw", TEXT, nullable=False),
        db.Column("metrics_raw", TEXT, nullable=False),
        db.Column("summary", TEXT, nullable=False),
        db.Column("metrics", TEXT, nullable=False),
    )
    return peloton_table

    


if __name__ == '__main__':
    main()