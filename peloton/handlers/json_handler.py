import json

from peloton.schema import PelotonWorkoutData
from peloton.constants import WORKOUTS_DIR, INSTRUCTORS_JSON


class PelotonJSONWriter():
    """
    A class that handles reading and writing Peloton workout data in JSON format.

    Attributes:
        - `json_files` (list[Path]): List of JSON files in the workout directory.
        - `total_workouts_on_disk` (int): Total number of workouts on disk.
        - `workout_ids` (list[str]): List of workout IDs extracted from JSON file names.
        - `all_workouts` (list[PelotonWorkoutData]): List of all workouts loaded from JSON files.
        - `instructors_dict` (dict): Dictionary of instructors loaded from JSON file.

    Methods:
        - `refresh_data()`: Refreshes the data by updating the attributes.
        - `get_json_file_list()`: Returns a list of JSON files in the workout directory.
        - `get_workout_ids_from_json()`: Returns a list of workout IDs extracted from JSON file names.
        - `get_workouts_from_json()`: Returns a list of PelotonWorkoutData objects loaded from JSON files.
        - `_get_workout_from_json(workout_id)`: Returns a PelotonWorkoutData object for the given workout ID.
        - `write_workout_to_json(workout)`: Writes a PelotonWorkoutData object to a JSON file.
        - `get_instructors_dict_from_json()`: Returns a dictionary of instructors loaded from JSON file.
        - `add_instructor_to_json(instructor)`: Adds an instructor to the JSON file.
    """

    def __init__(self):
        self.json_files = self.get_json_file_list()
        self.total_workouts_on_disk = len(self.json_files)
        self.workout_ids = self.get_workout_ids_from_json()
        self.all_workouts = self.get_workouts_from_json()
        self.instructors_dict = self.get_instructors_dict_from_json()

    def refresh_data(self):
        """
        Refreshes the data by updating the attributes.

        This method performs the following actions:
        - Retrieves the list of JSON files.
        - Updates the total number of workouts on disk.
        - Retrieves the workout IDs from the JSON files.
        - Retrieves all the workouts from the JSON files.
        - Retrieves the instructors dictionary from the JSON files.
        """
        self.json_files = self.get_json_file_list()
        self.total_workouts_on_disk = len(self.json_files)
        self.workout_ids = self.get_workout_ids_from_json()
        self.all_workouts = self.get_workouts_from_json()
        self.instructors_dict = self.get_instructors_dict_from_json()

    def get_json_file_list(self):
        """ Returns a list of the JSON files that exist in the workout directory. """
        try:
            return [file for file in WORKOUTS_DIR.iterdir()]
        except FileNotFoundError:
            return list()

    def get_workout_ids_from_json(self):
        """ Returns a list of workout IDs extracted from the JSON file names. """
        try:
            return [file.stem for file in self.json_files]
        except FileNotFoundError:
            return list()

    def get_workouts_from_json(self):
        """ Returns a list of `PelotonWorkoutData` objects loaded from JSON files. """
        if self.total_workouts_on_disk == 0:
            return list()
        else:
            return [self._get_workout_from_json(workout_id) for workout_id in self.workout_ids]

    def _get_workout_from_json(self, workout_id: str) -> PelotonWorkoutData:
        """
        - Returns a `PelotonWorkoutData` object for the given workout ID.

        Args:
            - `workout_id` (str): Workout ID.
        """
        with open(WORKOUTS_DIR.joinpath(f"{workout_id}.json"), 'r') as f:
            return PelotonWorkoutData.model_validate(json.load(f))

    def write_workout_to_json(self, workout: PelotonWorkoutData) -> None:
        """  Writes data from a `PelotonWorkoutData` object to a JSON file. """
        with open(WORKOUTS_DIR.joinpath(f"{workout.workout_id}.json"), 'w') as f:
            json.dump(workout.model_dump(), f, indent=4)
        self.refresh_data()
        
    def get_instructors_dict_from_json(self) -> dict:
        """ Returns a dictionary of instructors loaded from JSON file. """
        try:
            with open(INSTRUCTORS_JSON, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return dict()

    def add_instructor_to_json(self, instructor: dict) -> None:
        """
        - Adds an instructor to the JSON file.

        Args:
            - `instructor` (`dict`): Instructor information to be added.
        """
        instructors_dict = self.get_instructors_dict_from_json()
        instructors_dict.update({instructor['instructor_id']: instructor})
        with open(INSTRUCTORS_JSON, 'w') as f:
            json.dump(instructors_dict, f, indent=4)
        self.refresh_data()

def main():
    pass

if __name__ == '__main__':
    main()