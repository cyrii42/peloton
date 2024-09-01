import pandas as pd
import sqlalchemy as db
from gspread_pandas import Client, Spread

import peloton.constants as const
from trash.peloton_pivots import PelotonPivots
from peloton.peloton_processor import PelotonProcessor
from peloton.models.peloton_ride import PelotonRide, PelotonRideGroup

DATABASE = const.MARIADB_DATABASE
SQLITE_FILENAME = "sqlite:///data/peloton.db"


def main():
    sql_engine = db.create_engine(SQLITE_FILENAME)   # create_mariadb_engine(database=DATABASE)
    peloton_processor = PelotonProcessor(sql_engine)
    
    df_full = peloton_processor.df_processed

    peloton_pivots = PelotonPivots(df_full)
    df_year_table = peloton_pivots.year_table
    df_month_table = peloton_pivots.month_table
    df_totals_table = peloton_pivots.totals_table
    
    spread = Spread('XXXXXXXXXXXXXXXXXXXXXXX')

    spread.open_sheet("XXXXXXXXXXXXXXX")

    df = spread.sheet_to_df(index=None)

    print(df)
    

    # # Display available worksheets
    # spread.sheets

    # # Save DataFrame to worksheet 'New Test Sheet', create it first if it doesn't exist
    # spread.df_to_sheet(df, index=False, sheet='New Test Sheet', start='A1', replace=True)

    # Make columns bold!
    # spread.sheet.format('A1:AL1', {'textFormat': {'bold': True}})



if __name__ == "__main__":
    main()