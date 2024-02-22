import json
from pathlib import Path
from pprint import pprint


from peloton.schema import PelotonWorkoutData
from peloton.constants import EASTERN_TIME, WORKOUTS_DIR, INSTRUCTORS_JSON


class PelotonJSONWriter():
    def __init__(self):
        self.json_files = self.get_json_file_list()
        self.total_workouts_on_disk = len(self.json_files)
        self.workout_ids = self.get_workout_ids_from_json()
        self.all_workouts = self.get_workout_data_from_json()
        self.instructors_dict = self.get_instructors_dict_from_json()

    def refresh_data(self) -> None:
        self.json_files = self.get_json_file_list()
        self.total_workouts_on_disk = len(self.json_files)
        self.workout_ids = self.get_workout_ids_from_json()
        self.all_workouts = self.get_workout_data_from_json()
        self.instructors_dict = self.get_instructors_dict_from_json()

    def get_json_file_list(self) -> list[Path]:
        try:
            return [file for file in WORKOUTS_DIR.iterdir()]
        except FileNotFoundError:
            return list()

    def get_workout_ids_from_json(self) -> list[str]:
        try:
            return [file.stem for file in self.json_files]
        except FileNotFoundError:
            return list()

    def get_workout_from_json(self, workout_id: str) -> PelotonWorkoutData:
        with open(WORKOUTS_DIR.joinpath(f"{workout_id}.json"), 'r') as f:
            return PelotonWorkoutData.model_validate(json.load(f))

    def get_workout_data_from_json(self) -> list[PelotonWorkoutData]:
        if self.total_workouts_on_disk == 0:
            return list()
        else:
            return [self.get_workout_from_json(workout_id) for workout_id in self.workout_ids]

    def write_workout_to_json(self, workout: PelotonWorkoutData) -> None:
        with open(WORKOUTS_DIR.joinpath(f"{workout.workout_id}.json"), 'w') as f:
            json.dump(workout.model_dump(), f, indent=4)
        self.refresh_data()
        
    def get_instructors_dict_from_json(self) -> dict:
        try:
            with open(INSTRUCTORS_JSON, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return dict()

    def add_instructor_to_json(self, instructor: dict) -> None:
        instructors_dict = self.get_instructors_dict_from_json()
        instructors_dict.update({instructor['instructor_id']: instructor})
        with open(INSTRUCTORS_JSON, 'w') as f:
            json.dump(instructors_dict, f, indent=4)
        self.refresh_data()

def main():
    pass

if __name__ == '__main__':
    main()