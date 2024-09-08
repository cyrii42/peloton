import pandas as pd
import sqlalchemy as db

from peloton.helpers.constants import MARIADB_USER, MARIADB_PASS, MARIADB_SERVER


# SQL database functions
def create_mariadb_engine(database: str,
                          username: str = MARIADB_USER,
                          password: str = MARIADB_PASS,
                          host:str = MARIADB_SERVER) -> db.Engine:
    ''' Creates a SQLAlchemy engine for a locally hosted MariaDB server.'''
    
    mariadb_url = db.URL.create(
        drivername="mysql+pymysql",
        username=username,
        password=password,
        host=host,
        database=database,
    )
    return db.create_engine(mariadb_url)


def select_all_from_table(engine: db.Engine, table: str, 
                          index_col: str = None, parse_dates: list[str] = None
                          ) -> pd.DataFrame:
    with engine.connect() as conn:
        df = pd.read_sql(
            f"SELECT * from {table}", 
            conn, 
            index_col=index_col, 
            parse_dates=parse_dates
        )
    return df


def main():
    print("This is a module, not a script.")

if __name__ == '__main__':
    main