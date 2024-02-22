from dataclasses import dataclass

import pandas as pd
import sqlalchemy as db

from peloton.constants import PELOTON_CSV_DIR
from trash.peloton_data import PelotonData


@dataclass
class PelotonCSVWriter():
    peloton_data: PelotonData

    def write_csv_files(self) -> None:
        self.peloton_data.year_table.to_csv(f"{PELOTON_CSV_DIR}/year_table.csv")
        self.peloton_data.month_table.to_csv(f"{PELOTON_CSV_DIR}/month_table.csv")
        self.peloton_data.totals_table.to_csv(f"{PELOTON_CSV_DIR}/totals_table.csv")
        self.peloton_data.df_processed_workout_data.to_csv(f"{PELOTON_CSV_DIR}/processed_workouts_data.csv")
        self.peloton_data.df_raw_workouts_data.to_csv(f"{PELOTON_CSV_DIR}/raw_workouts_data.csv")
        self.peloton_data.df_raw_metrics_data.to_csv(f"{PELOTON_CSV_DIR}/raw_metrics_data.csv")