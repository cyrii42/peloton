import pandas as pd 
from peloton.schema import PelotonWorkoutData, PelotonPivots

from peloton.constants import DATA_DIR

    
class PelotonCSVWriter():
    def __init__(self, df_processed: pd.DataFrame):
        self.df_processed = df_processed
        self.pivots = PelotonPivots(df_processed)

    def write_csv_files(self) -> None:
        self.df_processed.to_csv(DATA_DIR.joinpath('processed_workouts_data.csv'))
        self.pivots.year_table.to_csv(DATA_DIR.joinpath('year_table.csv'))
        self.pivots.month_table.to_csv(DATA_DIR.joinpath('month_table.csv'))
        self.pivots.totals_table.to_csv(DATA_DIR.joinpath('totals_table.csv'))
        


def main():
    pass


if __name__ == '__main__':
    main()