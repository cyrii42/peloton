import pandas as pd

from peloton.helpers import create_mariadb_engine


def copy_tables_to_testing_database():
    engine_main = create_mariadb_engine("peloton")
    engine_test = create_mariadb_engine("peloton_test")

    with engine_main.connect() as conn:
        df_workouts_raw = pd.read_sql("SELECT * from raw_data_workouts", conn)
        df_metrics_raw  = pd.read_sql("SELECT * from raw_data_metrics", conn)
        df_processed = pd.read_sql("SELECT * from peloton", conn)

    with engine_test.connect() as conn:
        df_workouts_raw.to_sql("raw_data_workouts", conn, if_exists="replace", index=False)
        df_metrics_raw.to_sql("raw_data_metrics", conn, if_exists="replace", index=False)
        df_processed.to_sql("peloton", conn, if_exists="replace", index=False)


def copy_df_to_new_table_in_testing_database(input_df: pd.DataFrame, table: str, convert_dtypes: bool = False):
    if convert_dtypes:
        # Convert all datatypes (other than int64/float64/bool) to strings
        for column in input_df.select_dtypes(exclude=['int64', 'float64', 'bool']).columns:
            input_df[column] = input_df[column].astype("string")
        
    engine_test = create_mariadb_engine("peloton_test")
    with engine_test.connect() as conn:
        input_df.to_sql(table, conn, if_exists="replace", index=False)


def main():
    print("hi there -- this is a module file, not a script")


if __name__ == "__main__":
    main()