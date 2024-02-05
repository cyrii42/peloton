import argparse

import sqlalchemy as db

from peloton.constants import MARIADB_DATABASE
from peloton.helpers import create_mariadb_engine
from peloton.peloton_pivots import PelotonPivots
from peloton.peloton_processor import PelotonProcessor

SQLITE_FILENAME = "sqlite:///data/peloton.db"

parser = argparse.ArgumentParser()
parser.add_argument('-c', '--check-new-workouts', dest='CHECK_FOR_NEW_WORKOUTS',
                    action='store_const', const=True, default=False,
                    help='check for new workouts on remote Peloton database')
parser.add_argument('-m', '--update-mariadb', dest='UPDATE_MARIADB',
                    action='store_const',const=True, default=False,
                    help='update MariaDB database on local network')
args = parser.parse_args()


def main():
    sqlite_engine = db.create_engine(SQLITE_FILENAME)
    peloton_processor = PelotonProcessor(sqlite_engine)
    
    if args.CHECK_FOR_NEW_WORKOUTS:
        peloton_processor.check_for_new_workouts()

    peloton_processor.print_processed_data_to_stdout()

    pivots = PelotonPivots(peloton_processor)
    pivots.print_pivot_tables()
    if peloton_processor.new_workouts:
        pivots.write_csv_files()

    if args.UPDATE_MARIADB:
        print("\nUpdating MariaDB database...")
        mariadb_engine = create_mariadb_engine(database=MARIADB_DATABASE)

        mariadb_processor = PelotonProcessor(mariadb_engine)
        mariadb_processor.check_for_new_workouts()
        mariadb_processor.print_processed_data_to_stdout()
        
        mariadb_pivots = PelotonPivots(mariadb_processor)
        mariadb_pivots.print_pivot_tables()
    

if __name__ == "__main__":
    main()