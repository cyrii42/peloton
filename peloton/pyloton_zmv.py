import json
import time
from datetime import datetime
from pathlib import Path
from pprint import pprint

import requests
from pydantic import BaseModel, Field, field_serializer
from typing_extensions import Optional, Self

from .constants import (BASE_URL, EASTERN_TIME, INSTRUCTORS_JSON,
                        PELOTON_PASSWORD, PELOTON_USER_ID, PELOTON_USERNAME,
                        SESSION_JSON)
from .exceptions import PelotonInstructorNotFoundError


class PelotonSessionIDToken(BaseModel):
    session_id: str
    user_id: str
    created_at: Optional[datetime] = Field(default=datetime.now(tz=EASTERN_TIME))

    @classmethod
    def read_token_from_json(cls, filename: str = SESSION_JSON) -> Self | None:
        """ Factory method:  reads session ID from a JSON file and instantiates a new `PelotonSessionIDToken`. """
        
        print(f"\nReading tokens from {filename}...\n")
        with open(filename, "r") as file:
            token = cls.model_validate_json(file.read())
        return token

    @field_serializer('created_at', when_used='always')
    def convert_datetime_to_string(dt: datetime) -> str:
        return dt.isoformat(sep='T', timespec='seconds')

    def write_token_to_json(self, filename: str = SESSION_JSON) -> None:
        """ Writes this Peloton session ID token to a JSON file on the filesystem. """

        print(f"\nWriting token data to {filename}...")
        with open(filename, "w") as file:
            file.write(self.model_dump_json(indent=4))
        print("Done.")


class PylotonZMV():
    def __init__(self, username: str, password: str) -> None:
        self.username = username
        self.password = password
        self.session = None
        self.total_workouts_num = None

    def create_new_session(self) -> requests.Session:
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
        print("Getting new session ID and resuming in 3 seconds...")
        time.sleep(3)
        auth_login_url = f"{BASE_URL}/auth/login"
        auth_payload = {'username_or_email': self.username, 'password': self.password}
        headers = {'Content-Type': 'application/json', 'User-Agent': 'pyloton'}
        resp = self.session.post(url=auth_login_url,json=auth_payload, headers=headers, timeout=10)
        resp.raise_for_status()
        
        self.login_token = PelotonSessionIDToken(session_id=resp.json()['session_id'], 
                                                 user_id=resp.json()['user_id'])
        self.login_token.write_token_to_json()
        self.session.cookies.set('peloton_session_id', self.login_token.session_id)

    def get_total_workouts_num(self) -> int:
        if self.session is None:
            self.create_new_session()
        try:
            resp = self.session.get(f"{BASE_URL}/api/me", timeout=10)
            resp.raise_for_status()
            return resp.json()["total_workouts"]
        except requests.HTTPError:
            self.get_new_login_token()
            resp = self.session.get(f"{BASE_URL}/api/me", timeout=10)
            resp.raise_for_status()
            return resp.json()["total_workouts"]

    def get_workout_ids(self, num_workouts: int = None) -> list[str]:
        if self.session is None:
            self.create_new_session()
        if num_workouts is None:
            num_workouts = (self.get_total_workouts_num() if self.total_workouts_num is None 
                                                    else self.total_workouts_num)

        limit = min(100, num_workouts)
        pages = (1 if limit < 100 
                   else ((num_workouts // limit) + min(1, (num_workouts % limit))))
           
        base_workout_url = f"{BASE_URL}/api/user/{PELOTON_USER_ID}/workouts?sort_by=-created"
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
        if self.session is None:
            self.create_new_session()
        url = f"{BASE_URL}/api/workout/{workout_id}"
        try:
            resp = self.session.get(url, timeout=10)
            resp.raise_for_status()
        except requests.HTTPError:
            self.get_new_login_token()
            resp = self.session.get(url, timeout=10)
            resp.raise_for_status()
            
        output_dict = resp.json()
        output_dict.update({'workout_id': workout_id}) 
        return output_dict

    def get_workout_metrics_by_id(self, workout_id: str, frequency: int = 60) -> dict:
        if self.session is None:
            self.create_new_session()
        url = f"{BASE_URL}/api/workout/{workout_id}/performance_graph?every_n={frequency}"
        try:
            resp = self.session.get(url, timeout=10)
            resp.raise_for_status()
        except requests.HTTPError:
            self.get_new_login_token()
            resp = self.session.get(url, timeout=10)
            resp.raise_for_status()
            
        output_dict = resp.json()
        output_dict.update({'workout_id': workout_id}) 
        return output_dict

    def get_user_id(self) -> str:
        if self.session is None:
            self.create_new_session()
        try:
            resp = self.session.get(f"{BASE_URL}/api/me", timeout=10)
            resp.raise_for_status()
            return resp.json()["id"]
        except requests.HTTPError:
            self.get_new_login_token()
            resp = self.session.get(f"{BASE_URL}/api/me", timeout=10)
            resp.raise_for_status()
            return resp.json()["id"]

    def get_all_instructors(self) -> dict:
        if self.session is None:
            self.create_new_session()
        try:
            resp = self.session.get(f"{BASE_URL}/api/instructor?page=0&limit=100", timeout=10)
            resp.raise_for_status()
            return resp.json()
        except requests.HTTPError:
            self.get_new_login_token()
            resp = self.session.get(f"{BASE_URL}/api/instructor?page=0&limit=100", timeout=10)
            resp.raise_for_status()
            return resp.json()

    def get_instructor_by_id(self, instructor_id: str) -> dict | None:
        if self.session is None:
            self.create_new_session()
            
        url = f"{BASE_URL}/api/instructor/{instructor_id}"
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
    #     url = f"{BASE_URL}/api/instructor/{instructor_id}"
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