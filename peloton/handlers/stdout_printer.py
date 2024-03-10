from datetime import datetime

import pandas as pd

from peloton.schema import PelotonPivots
from peloton.constants import EASTERN_TIME


class PelotonStdoutPrinter():
    def __init__(self, df_processed: pd.DataFrame):
        self.df_processed = df_processed
        self.pivots = PelotonPivots(df_processed)

    def regenerate_tables(self, new_df_processed: pd.DataFrame) -> None:
        self.df_processed = new_df_processed
        self.pivots = PelotonPivots(new_df_processed)
        
    def print_processed_data(self) -> None:
        df = self.df_processed.copy()
        if isinstance(df['start_time'].dtype, pd.DatetimeTZDtype):
            df['start_time_strf'] = [x.tz_convert(EASTERN_TIME).strftime('%a %h %d %I:%M %p') 
                                        for x in df['start_time'].tolist()]
        else:
            df['start_time_strf'] = [datetime.fromisoformat(x).strftime('%a %h %d %I:%M %p') 
                                        for x in df['start_time'].tolist()]
        print("")
        print(df[['start_time_strf', 'title', 'instructor_name', 'total_output', 
                    'distance', 'calories', 'avg_heart_rate', 'effort_score']].tail(15))

    def print_pivot_tables(self) -> None:
        print("")
        print("                             GRAND TOTALS")
        print(self.pivots.totals_table)
        print("")
        print(self.pivots.year_table)
        print("")
        print(self.pivots.month_table)