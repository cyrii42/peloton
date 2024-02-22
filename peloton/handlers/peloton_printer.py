from datetime import datetime
from zoneinfo import ZoneInfo

import pandas as pd

from peloton.schema import PelotonPivots


class PelotonStdoutPrinter():
    def __init__(self, df_processed: pd.DataFrame):
        self.df_processed = df_processed
        self.pivots = PelotonPivots(df_processed)

    def regenerate_tables(self, new_df_processed: pd.DataFrame) -> None:
        self.df_processed = new_df_processed
        self.pivots = PelotonPivots(new_df_processed)
        
    def print_processed_data(self) -> None:
        df = self.df_processed
        if isinstance(df['start_time_iso'].dtype, pd.DatetimeTZDtype):
            df['start_time_strf'] = [x.tz_convert(ZoneInfo("America/New_York")).strftime('%a %h %d %I:%M %p') 
                                        for x in df['start_time_iso'].tolist()]
        else:
            df['start_time_strf'] = [datetime.fromisoformat(x).strftime('%a %h %d %I:%M %p') 
                                        for x in df['start_time_iso'].tolist()]
        print("")
        print(df[['start_time_strf', 'ride_title', 'instructor_name', 'total_output', 
                    'distance', 'calories', 'heart_rate_avg', 'strive_score']].tail(15))

    def print_pivot_tables(self) -> None:
        print("")
        print("                             GRAND TOTALS")
        print(self.pivots.totals_table)
        print("")
        print(self.pivots.year_table)
        print("")
        print(self.pivots.month_table)