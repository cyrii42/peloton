from dataclasses import dataclass

from peloton.schema import PelotonWorkoutData

from peloton.constants import PELOTON_CSV_DIR, EASTERN_TIME, WORKOUTS_DIR, INSTRUCTORS_JSON



    
@dataclass
class PelotonCSVWriter():
    peloton_data: PelotonWorkoutData

    def write_csv_files(self) -> None:
        self.peloton_data.year_table.to_csv(f"{PELOTON_CSV_DIR}/year_table.csv")
        self.peloton_data.month_table.to_csv(f"{PELOTON_CSV_DIR}/month_table.csv")
        self.peloton_data.totals_table.to_csv(f"{PELOTON_CSV_DIR}/totals_table.csv")
        self.peloton_data.df_processed_workout_data.to_csv(f"{PELOTON_CSV_DIR}/processed_workouts_data.csv")
        self.peloton_data.df_raw_workouts_data.to_csv(f"{PELOTON_CSV_DIR}/raw_workouts_data.csv")
        self.peloton_data.df_raw_metrics_data.to_csv(f"{PELOTON_CSV_DIR}/raw_metrics_data.csv")


def main():
    pass


if __name__ == '__main__':
    main()