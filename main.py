import argparse

import sqlalchemy as db

import peloton.constants as const
from peloton.helpers import create_mariadb_engine
from peloton.peloton_pivots import PelotonPivots, PivotCSVWriter
from peloton.peloton_processor import PelotonProcessor


DATABASE = const.MARIADB_DATABASE
SQLITE_FILENAME = "sqlite:///data/peloton.db"

parser = argparse.ArgumentParser()
parser.add_argument('-c', '--check-new-workouts', dest='CHECK_FOR_NEW_WORKOUTS', action='store_const',
                    const=True, default=False,
                    help='check for new workouts on remote Peloton database')
args = parser.parse_args()


def main():
    # sql_engine = create_mariadb_engine(database=DATABASE)
    sql_engine = db.create_engine(SQLITE_FILENAME)

    peloton_processor = PelotonProcessor(sql_engine)
    
    if args.CHECK_FOR_NEW_WORKOUTS:
        peloton_processor.check_for_new_workouts()

    # Whether or not there are new workouts, pull the full processed dataset from SQL and print to terminal
    peloton_processor.print_processed_data_to_stdout()

    # Print pivot tables
    pivots = PelotonPivots(peloton_processor.df_processed_workouts_data_in_sql)
    pivots.print_pivot_tables()

    # If there are new workouts, write pivot tables to CSV
    if peloton_processor.new_workouts:
        pivot_csv_writer = PivotCSVWriter(pivots, peloton_processor)
        pivot_csv_writer.write_csv_files()
    
    
    

       
if __name__ == "__main__":
    main()