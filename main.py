import argparse

import sqlalchemy as db

from peloton.helpers import create_mariadb_engine
from peloton import PelotonProcessor

SQLITE_FILENAME = "sqlite:///data/peloton.db"
MARIADB_DATABASE = "peloton"

parser = argparse.ArgumentParser()
parser.add_argument('-c', '--check-new-workouts', dest='CHECK_FOR_NEW_WORKOUTS',
                    action='store_const', const=True, default=False,
                    help='check for new workouts on remote Peloton database')
parser.add_argument('-m', '--update-mariadb', dest='UPDATE_MARIADB',
                    action='store_const',const=True, default=False,
                    help='update MariaDB database on local network')
args = parser.parse_args()


def main():
    if not args.UPDATE_MARIADB:
        sqlite_engine = db.create_engine(SQLITE_FILENAME)
        peloton_processor = PelotonProcessor(sqlite_engine)
        
        if args.CHECK_FOR_NEW_WORKOUTS:
            peloton_processor.check_for_new_workouts()

        peloton_processor.print_processed_data_to_stdout()
        peloton_processor.print_pivot_tables_to_stdout()

        if peloton_processor.new_workouts:
            peloton_processor.write_csv_files()

    else:
        print("Updating MariaDB database...\n")
        mariadb_engine = create_mariadb_engine(database=MARIADB_DATABASE)

        mariadb_processor = PelotonProcessor(mariadb_engine)
        mariadb_processor.check_for_new_workouts()
        
        mariadb_processor.print_processed_data_to_stdout()
        mariadb_processor.print_pivot_tables_to_stdout()

    

if __name__ == "__main__":
    main()