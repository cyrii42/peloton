import json
from pathlib import Path
from pprint import pprint
from zoneinfo import ZoneInfo

from trash.pyloton_models import PelotonWorkoutData
from peloton_exceptions import PelotonInstructorNotFoundError

EASTERN_TIME = ZoneInfo('America/New_York')
WORKOUTS_DIR = Path('../data/workouts').resolve()
INSTRUCTORS_JSON = Path('..').resolve().joinpath('peloton_instructors.json')

class PelotonJSONWriter():
    def __init__(self):
        try:
            self.json_files = [file for file in WORKOUTS_DIR.iterdir()]
            self.workout_ids = [file.stem for file in WORKOUTS_DIR.iterdir()]
        except FileNotFoundError:
            self.json_files = list()
            self.workout_ids = list()
            
        self.total_workouts_on_disk = len(self.json_files)
        self.all_workouts = self.get_all_json_workouts()

    def get_workout_from_json(self, workout_id: str) -> PelotonWorkoutData:
        with open(WORKOUTS_DIR.joinpath(f"{workout_id}.json"), 'r') as f:
            return PelotonWorkoutData.model_validate(json.load(f))

    def get_all_json_workouts(self) -> list[PelotonWorkoutData]:
        if self.total_workouts_on_disk == 0:
            return list()
        else:
            return [self.get_workout_from_json(workout_id) for workout_id in self.workout_ids]

    def write_workout_to_json(self, workout: PelotonWorkoutData) -> None:
        with open(WORKOUTS_DIR.joinpath(f"{workout.workout_id}.json"), 'w') as f:
            json.dump(workout.model_dump(), f, indent=4)

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



def main():
    json_writer = PelotonJSONWriter()
    # asdf = json_writer.get_workout_from_json('9ae7e95d7087420a8fe1a8393fb11d1f')
    # pprint(asdf)

    asdf = json_writer.get_instructors_dict_from_json()
    print(asdf)


if __name__ == '__main__':
    main()