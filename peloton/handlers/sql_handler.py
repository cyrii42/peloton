from pathlib import Path
from pprint import pprint


import pandas as pd
import sqlalchemy as db
from peloton.constants import EASTERN_TIME, WORKOUTS_DIR, INSTRUCTORS_JSON



class PelotonSQL():
    def __init__(self, sql_engine: db.Engine):
        self.sql_engine = sql_engine

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
