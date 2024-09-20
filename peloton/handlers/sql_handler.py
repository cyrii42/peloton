import json

import sqlalchemy as db
from sqlalchemy.dialects.sqlite import TEXT

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

    def get_workout_id_list(self) -> list[str]: ...

    def ingest_workouts(self) -> list[PelotonWorkoutData]:
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

    def export_workout(self, workout: PelotonWorkoutData) -> None:
        with self.sql_engine.connect() as conn:
            conn.execute(
                db.insert(self.peloton_table).values(workout.model_dump_json())
            )
            conn.commit()

    def update_workout(self, workout: PelotonWorkoutData) -> None: ...
    def get_workout(self, workout_id: str) -> PelotonWorkoutData: ...
    def get_instructor(self, instructor_id: str) -> dict: ...
    def add_instructor(self, instructor: dict) -> None: ...  
