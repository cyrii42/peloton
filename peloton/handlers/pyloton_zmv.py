import time
from datetime import datetime

import requests
from pydantic import BaseModel, Field, field_serializer
from typing_extensions import Optional, Self

from peloton.helpers.constants import (PELOTON_BASE_URL, EASTERN_TIME,
                        PELOTON_USER_ID, SESSION_JSON)
                        
from peloton.helpers.exceptions import PelotonInstructorNotFoundError


class PelotonSessionIDToken(BaseModel):
    """
    Represents a Peloton session ID token.

    Attributes:
        - `session_id` (str): The session ID.
        - `user_id` (str): The user ID.
        - `created_at` (Optional[datetime]): The creation timestamp of the token. Defaults to the current datetime in the Eastern Time zone.

    """

    session_id: str
    user_id: str
    created_at: Optional[datetime] = Field(default=datetime.now(tz=EASTERN_TIME))

    @classmethod
    def read_token_from_json(cls, filename: str = SESSION_JSON) -> Self | None:
        """ Factory method: reads session ID from a JSON file and instantiates a new `PelotonSessionIDToken`.

        Args:
            filename (str, optional): The path to the JSON file containing the session ID token. Defaults to SESSION_JSON.

        Returns:
            Self | None: An instance of `PelotonSessionIDToken` if the token is successfully read from the file, 
            otherwise None.

        """
        print(f"\nReading tokens from {filename}...\n")
        with open(filename, "r") as file:
            token = cls.model_validate_json(file.read())
        return token

    @field_serializer('created_at', when_used='always')
    def convert_datetime_to_string(dt: datetime) -> str:
        """ Converts a datetime object to a string representation in ISO 8601 format. """
        return dt.isoformat(sep='T', timespec='seconds')

    def write_token_to_json(self, filename: str = SESSION_JSON) -> None:
        """  Writes this Peloton session ID token to a JSON file on the filesystem. """

        print(f"\nWriting token data to {filename}...")
        with open(filename, "w") as file:
            file.write(self.model_dump_json(indent=4))
        print("Done.")


class PylotonZMV():
    """
    A class representing an object for connecting to Peloton and retrieving data.

    Attributes:
        - `username` (str): The username for authentication.
        - `password` (str): The password for authentication.
        - `session` (`requests.Session`): The session object for making HTTP requests.
        - `total_workouts_num` (int): The total number of workouts.

    Methods:
        - `create_new_session()`:
            Creates a new session and sets the login token.

        - `get_new_login_token()`:
            Retrieves a new login token and sets it in the session.

        - `get_total_workouts_num()`:
            Retrieves the total number of workouts for the user.

        - `get_workout_ids()`:
            Retrieves a list of workout IDs.

        - `get_workout_summary_by_id()`:
            Retrieves the summary of a workout by its ID.

        - `get_workout_metrics_by_id()`:
            Retrieves the metrics of a workout by its ID.

        - `get_user_id()`:
            Retrieves the user ID.

        - `get_all_instructors()`:
            Retrieves a dictionary of all instructors.

        - `get_instructor_by_id()`:
            Retrieves the details of an instructor by their ID.

    """
    def __init__(self, username: str, password: str) -> None:
        self.username = username
        self.password = password
        self.session = None
        self.total_workouts_num = None

    def create_new_session(self) -> requests.Session:
        """ Creates a new session and sets the login token. """
        
        self.session = requests.Session()
        try:
            self.login_token = PelotonSessionIDToken.read_token_from_json()
        except FileNotFoundError:
            print("JSON file not found.  Getting new login token...")
            self.get_new_login_token()
        except KeyError:
            print("Key error in JSON file.  Getting new login token...")
            self.get_new_login_token()
        else:
            self.session.cookies.set('peloton_session_id', self.login_token.session_id)

    def get_new_login_token(self) -> None:
        """ Retrieves a new login token and sets it in the session. """
        
        print("Getting new session ID and resuming in 3 seconds...")
        time.sleep(3)
        auth_login_url = f"{PELOTON_BASE_URL}/auth/login"
        auth_payload = {'username_or_email': self.username, 'password': self.password}
        headers = {'Content-Type': 'application/json', 'User-Agent': 'pyloton'}
        resp = self.session.post(url=auth_login_url,json=auth_payload, headers=headers, timeout=10)
        resp.raise_for_status()
        
        self.login_token = PelotonSessionIDToken(session_id=resp.json()['session_id'], 
                                                 user_id=resp.json()['user_id'])
        self.login_token.write_token_to_json()
        self.session.cookies.set('peloton_session_id', self.login_token.session_id)

    def get_total_workouts_num(self) -> int:
        """ Retrieves the total number of workouts for the user. """
        
        if self.session is None:
            self.create_new_session()
        try:
            resp = self.session.get(f"{PELOTON_BASE_URL}/api/me", timeout=10)
            resp.raise_for_status()
            return resp.json()["total_workouts"]
        except requests.HTTPError:
            self.get_new_login_token()
            resp = self.session.get(f"{PELOTON_BASE_URL}/api/me", timeout=10)
            resp.raise_for_status()
            return resp.json()["total_workouts"]

    def get_workout_ids(self, num_workouts: int = None) -> list[str]:
        """ Retrieves a list of workout IDs.

        Args:
            - `num_workouts` (int, optional): The number of workouts to retrieve. If not provided, retrieves all workouts.
        """
        
        if self.session is None:
            self.create_new_session()
        if num_workouts is None:
            num_workouts = (self.get_total_workouts_num() if self.total_workouts_num is None 
                                                    else self.total_workouts_num)

        limit = min(100, num_workouts)
        pages = (1 if limit < 100 
                   else ((num_workouts // limit) + min(1, (num_workouts % limit))))
           
        base_workout_url = f"{PELOTON_BASE_URL}/api/user/{PELOTON_USER_ID}/workouts?sort_by=-created"
        workout_id_list = []
        for page in range(pages):
            url = f"{base_workout_url}&page={page}&limit={limit}"
            try:
                resp = self.session.get(url, timeout=10)
                resp.raise_for_status()
            except requests.HTTPError:
                self.get_new_login_token()
                resp = self.session.get(url, timeout=10)
                resp.raise_for_status()
                
            for dataset in resp.json()['data']:
                workout_id_list.append(dataset['id'])

        return workout_id_list

    def get_workout_summary_by_id(self, workout_id: str) -> dict:
        """
        Retrieves the summary of a workout by its ID.

        Args:
            - `workout_id` (str): The ID of the workout.
        """
        
        if self.session is None:
            self.create_new_session()
        url = f"{PELOTON_BASE_URL}/api/workout/{workout_id}"
        try:
            resp = self.session.get(url, timeout=10)
            resp.raise_for_status()
        except requests.HTTPError:
            self.get_new_login_token()
            resp = self.session.get(url, timeout=10)
            resp.raise_for_status()
            
        output_dict: dict = resp.json()
        output_dict.update({'workout_id': workout_id}) 
        return output_dict

    def get_workout_metrics_by_id(self, workout_id: str, frequency: int = 5) -> dict:
        """
        Retrieves the metrics of a workout by its ID.

        Args:
            - `workout_id` (str): The ID of the workout.
            - `frequency` (int, optional): The frequency of the metrics data points. Default is 5.
        """
        
        if self.session is None:
            self.create_new_session()
        url = f"{PELOTON_BASE_URL}/api/workout/{workout_id}/performance_graph?every_n={frequency}"
        try:
            resp = self.session.get(url, timeout=10)
            resp.raise_for_status()
        except requests.HTTPError:
            self.get_new_login_token()
            resp = self.session.get(url, timeout=10)
            resp.raise_for_status()
            
        output_dict: dict = resp.json()
        output_dict.update({'workout_id': workout_id}) 
        return output_dict

    def get_user_id(self) -> str:
        """ Retrieves the user ID. """
        if self.session is None:
            self.create_new_session()
        try:
            resp = self.session.get(f"{PELOTON_BASE_URL}/api/me", timeout=10)
            resp.raise_for_status()
            return resp.json()["id"]
        except requests.HTTPError:
            self.get_new_login_token()
            resp = self.session.get(f"{PELOTON_BASE_URL}/api/me", timeout=10)
            resp.raise_for_status()
            return resp.json()["id"]

    def get_all_instructors(self) -> dict:
        """ Retrieves a dictionary of all instructors. """
        if self.session is None:
            self.create_new_session()
        try:
            resp = self.session.get(f"{PELOTON_BASE_URL}/api/instructor?page=0&limit=100", timeout=10)
            resp.raise_for_status()
            return resp.json()
        except requests.HTTPError:
            self.get_new_login_token()
            resp = self.session.get(f"{PELOTON_BASE_URL}/api/instructor?page=0&limit=100", timeout=10)
            resp.raise_for_status()
            return resp.json()

    def get_instructor_by_id(self, instructor_id: str) -> dict | None:
        """
        Retrieves the details of an instructor by their ID.

        Args:
            - `instructor_id` (str): The ID of the instructor.
        """
        
        if self.session is None:
            self.create_new_session()
            
        url = f"{PELOTON_BASE_URL}/api/instructor/{instructor_id}"
        try:
            resp = self.session.get(url, timeout=10)
            resp.raise_for_status()
        except requests.HTTPError:
            if resp.status_code == 401:
                self.get_new_login_token()
                resp = self.session.get(url, timeout=10)
                resp.raise_for_status()
            elif resp.status_code == 404:
                raise PelotonInstructorNotFoundError(f"Instructor ID '{instructor_id}' not found.")
            else:
                raise requests.HTTPError
            
        instructor_data = resp.json()
        return instructor_data


def main():
    pass

if __name__ == '__main__':
    main()





# @dataclass
# class PelotonSessionIDToken():
#     session_id: str
#     user_id: str
#     created_at: datetime = datetime.now(tz=EASTERN_TIME)

#     def write_session_id_json(self, filename: str = SESSION_JSON) -> None:
#         """ Writes this Peloton session ID token to a JSON file on the filesystem. """
#         tokens_dict = asdict(self)
#         tokens_dict = { x: (y.isoformat() if isinstance(y, datetime) else y) for (x, y) in tokens_dict.items() }

#         print(f"\nWriting token data to {filename}...")
#         with open(filename, "w") as file:
#             json.dump(tokens_dict, file, indent=4)
#         print("Done.")

#     @classmethod
#     def read_session_id_from_json(cls, filename: str = SESSION_JSON) -> Self | None:
#         """ Factory method:  reads session ID from a JSON file and instantiates a new `PelotonSessionIDToken`. """
        
#         print(f"\nReading tokens from {filename}...\n")

#         with open(filename, "r") as file:
#             tokens_dict = json.load(file)
#         session_id = tokens_dict['session_id']
#         user_id = tokens_dict['user_id']
#         created_at = datetime.fromisoformat(tokens_dict['created_at']).astimezone(tz=EASTERN_TIME)

#         session_token = cls(session_id=session_id, 
#                             user_id=user_id, 
#                             created_at=created_at)
#         return session_token




    # def get_instructor_by_id(self, instructor_id: str, skip_json: bool = False) -> dict | None:
    #     if not skip_json:
    #         try:
    #             with open(INSTRUCTORS_JSON, 'r') as f:
    #                 instructors_dict = json.load(f)
    #         except FileNotFoundError:
    #             instructors_dict = dict()
    #         if instructor_id in instructors_dict.keys():
    #             return instructors_dict[instructor_id]

    #     if self.session is None:
    #         self.create_session()
    #     url = f"{PELOTON_BASE_URL}/api/instructor/{instructor_id}"
    #     try:
    #         resp = self.session.get(url, timeout=10)
    #         resp.raise_for_status()
    #     except requests.HTTPError:
    #         if resp.status_code == 401:
    #             self.get_new_login_token()
    #             resp = self.session.get(url, timeout=10)
    #             resp.raise_for_status()
    #         elif resp.status_code == 404:
    #             raise PelotonInstructorNotFoundError(f"Instructor ID '{instructor_id}' not found.")
    #         else:
    #             raise requests.HTTPError
    #     instructor_data = resp.json()
    #     if not skip_json:
    #         instructors_dict.update({instructor_id: instructor_data['instructor_id']})
    #         with open(INSTRUCTORS_JSON, 'w') as f:
    #             json.dump(instructors_dict, f)
    #     return instructor_data