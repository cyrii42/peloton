import json
from pathlib import Path
from pprint import pprint

import pandas as pd
import sqlalchemy as db
from sqlalchemy.dialects.sqlite import TEXT

from peloton.constants import EASTERN_TIME, INSTRUCTORS_JSON, WORKOUTS_DIR
from peloton.schema import PelotonMetrics, PelotonSummary, PelotonWorkoutData

metadata_obj = db.MetaData()

class PelotonSQL():
    def __init__(self, sql_engine: db.Engine, table_name: str = "peloton_json"):
        self.sql_engine = sql_engine
        self.peloton_table = self.create_table(table_name)

    def create_table(self, table_name: str) -> db.Table:
        peloton_table = db.Table(
            table_name,
            metadata_obj,
            db.Column("workout_id", TEXT, primary_key=True),
            db.Column("summary_raw", TEXT, nullable=False),
            db.Column("metrics_raw", TEXT, nullable=False),
            db.Column("summary", TEXT, nullable=False),
            db.Column("metrics", TEXT, nullable=False),
        )
        return peloton_table

    def ingest_workouts_from_sql(self) -> list[PelotonWorkoutData]:
        print("getting workouts from SQL")
        stmt = db.select(self.peloton_table)
        with self.sql_engine.connect() as conn:
            workouts = [row for row in conn.execute(stmt)]
        
        return [PelotonWorkoutData(
            workout_id=workout[0],
            summary_raw=json.loads(workout[1]),
            metrics_raw=json.loads(workout[2]),
            summary=PelotonSummary.model_validate_json(workout[3]),
            metrics=PelotonMetrics.model_validate_json(workout[4])
        ) for workout in workouts]

    def export_workout_to_sql(self, workout: PelotonWorkoutData) -> None:
        with self.sql_engine.connect() as conn:
            conn.execute(
                db.insert(self.peloton_table).values(workout.model_dump_json())
            )
            conn.commit()

    def export_df_to_sql(self, input_df: pd.DataFrame, table_name: str) -> None:
        df = input_df.copy()
        
        for column in df.select_dtypes(exclude=['int64', 'float64', 'bool']).columns:
            df[column] = df[column].astype("string")
            
        with self.sql_engine.connect() as conn:
            df.to_sql(table_name, conn, if_exists="append", index=False)

    def ingest_df_from_sql(self, table_name: str) -> pd.DataFrame:
        with self.sql_engine.connect() as conn:
            df = pd.read_sql(f"SELECT * from {table_name}", conn)
            
        return df

    def make_workout_dict(self, workout: PelotonWorkoutData) -> dict:
        return {
            "workout_id": workout.workout_id,
            "summary_raw": json.dumps(workout.summary_raw),
            "metrics_raw": json.dumps(workout.metrics_raw),
            "summary": workout.summary.model_dump_json(),
            "metrics": workout.metrics.model_dump_json(),
        }

    def get_processed_df_from_sql(self) -> pd.DataFrame:
        with self.sql_engine.connect() as conn:
            df = pd.read_sql("SELECT * from processed_df", conn)
        return df

    def append_processed_df_to_sql(self, processed_df: pd.DataFrame) -> None:
        with self.sql_engine.connect() as conn:
            processed_df.to_sql("processed_df", conn, if_exists="append", index=False)