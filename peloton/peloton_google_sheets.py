from dataclasses import dataclass, field

from gspread_pandas import Spread

from . import PELOTON_SPREADSHEET, PelotonProcessor


@dataclass
class PelotonGoogleSheetsWriter():
    data: PelotonProcessor
    spread: Spread = field(init=False)

    def __post_init__(self):
        self.spread = Spread(PELOTON_SPREADSHEET)

    def write_to_google_sheet(self) -> None:
        worksheets = {
            'Processed Data': self.data.ingest_processed_data_from_sql(),
            'Raw Metrics Data': self.data.ingest_raw_metrics_data_from_sql(),
            'Raw Workouts Data': self.data.ingest_raw_workout_data_from_sql(),
            'Year Table': self.data.pivots.year_table,
            'Month Table': self.data.pivots.month_table,
            'Totals Table': self.data.pivots.totals_table
        }

        for sheet_name, sheet_df in worksheets.items():
            last_existing_row = sheet_df.shape[0] + 1
            starting_row = last_existing_row + 1

            self.spread.df_to_sheet(sheet_df, 
                               sheet=sheet_name, 
                               replace=True, 
                               index=False, 
                               headers=True, 
                               freeze_headers=True, 
                               start=(1, 1))