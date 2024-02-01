import argparse

import sqlalchemy as db

import peloton.constants as const
from peloton.helpers import create_mariadb_engine
from peloton.peloton_pivots import PelotonPivots
from peloton.peloton_processor import PelotonProcessor

DATABASE = const.MARIADB_DATABASE
SQLITE_FILENAME = "sqlite:///data/peloton.db"

parser = argparse.ArgumentParser()
parser.add_argument('-c', '--check-new-workouts', dest='CHECK_FOR_NEW_WORKOUTS', action='store_const',
                    const=True, default=False,
                    help='check for new workouts on remote Peloton database')
args = parser.parse_args()

def main():
    sql_engine = db.create_engine(SQLITE_FILENAME)   # create_mariadb_engine(database=DATABASE)
    peloton_processor = PelotonProcessor(sql_engine)
    
    if args.CHECK_FOR_NEW_WORKOUTS:
        peloton_processor.check_for_new_workouts()

    peloton_processor.print_processed_data_to_stdout()

    pivots = PelotonPivots(peloton_processor)
    pivots.print_pivot_tables()
    if peloton_processor.new_workouts:
        pivots.write_csv_files()
    

if __name__ == "__main__":
    main()