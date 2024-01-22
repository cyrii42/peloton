import pandas as pd
import sqlalchemy as db

import peloton.constants as const

DATABASE = const.MARIADB_DATABASE


def create_mariadb_engine(database: str) -> db.Engine:
    mariadb_url = db.URL.create(
        drivername="mysql+pymysql",
        username=const.MARIADB_USER,
        password=const.MARIADB_PASS,
        host=const.MARIADB_SERVER,
        database=database,
    )
    return db.create_engine(mariadb_url)


def export_raw_workout_data_to_sql(input_df: pd.DataFrame, engine: db.Engine):
    # Convert all datatypes (other than int64/float64) to strings for subsequent SQL export
    for column in input_df.select_dtypes(exclude=['int64', 'float64', 'bool']).columns:
        input_df[column] = input_df[column].astype("string")

    with engine.connect() as conn:
        input_df.to_sql("raw_data_workouts", conn, if_exists="append", index=False)


def export_raw_metrics_data_to_sql(input_df: pd.DataFrame, engine: db.Engine):
    # Convert all datatypes (other than int64/float64) to strings for subsequent SQL export
    for column in input_df.select_dtypes(exclude=['int64', 'float64', 'bool']).columns:
        input_df[column] = input_df[column].astype("string")
        
    with engine.connect() as conn:
        input_df.to_sql("raw_data_metrics", conn, if_exists="append", index=False)


def export_processed_data_to_sql(input_df: pd.DataFrame, engine: db.Engine):
    with engine.connect() as conn:
        input_df.to_sql("peloton", conn, if_exists="append", index=False)


def ingest_raw_workout_data_from_sql(engine: db.Engine) -> pd.DataFrame:
    with engine.connect() as conn:
        df = pd.read_sql("SELECT * from raw_data_workouts", conn)
    return df


def ingest_raw_metrics_data_from_sql(engine: db.Engine) -> pd.DataFrame:
    with engine.connect() as conn:
        df = pd.read_sql("SELECT * from raw_data_metrics", conn)
    return df


def ingest_processed_data_from_sql(engine: db.Engine) -> pd.DataFrame:
    with engine.connect() as conn:
        df = pd.read_sql("SELECT * from peloton", conn)
    return df


def main():
    sql_engine = create_mariadb_engine(database=DATABASE)
    sqlite_engine = db.create_engine("sqlite://../data/peloton.db")

    df_raw_workouts_data_in_sql = ingest_raw_workout_data_from_sql(sql_engine)
    export_raw_workout_data_to_sql(df_raw_workouts_data_in_sql, sqlite_engine)

    df_raw_metrics_data_in_sql = ingest_raw_metrics_data_from_sql(sql_engine)
    export_raw_metrics_data_to_sql(df_raw_metrics_data_in_sql, sqlite_engine)

    df_processed_workouts_data_in_sql = ingest_processed_data_from_sql(sql_engine)
    export_processed_data_to_sql(df_processed_workouts_data_in_sql, sqlite_engine)

    

       
if __name__ == "__main__":
    main()
