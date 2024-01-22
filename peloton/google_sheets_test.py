import pandas as pd
from gspread_pandas import Client, Spread

import peloton.constants as const
import peloton.functions as func
import peloton.helpers as helpers
import peloton.peloton_pivots as pivots


def main():
    SQL_DB = "peloton"

    sql_engine = helpers.create_mariadb_engine(SQL_DB)

    df = helpers.ingest_processed_data_from_sql(sql_engine)

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