import json
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
from pprint import pprint

import requests
from constants import PELOTON_PASSWORD, PELOTON_USERNAME
from typing_extensions import Self

BASE_URL = "https://api.onepeloton.com"
EASTERN_TIME = ZoneInfo('America/New_York')
SESSION_JSON = Path('..').resolve().joinpath('session_id.json')

@dataclass
class PelotonSessionIDToken():
    session_id: str
    user_id: str
    created_at: datetime = datetime.now(tz=EASTERN_TIME)

    def write_session_id_json(self, filename: str = SESSION_JSON) -> None:
        """ Writes this Peloton session ID token to a JSON file on the filesystem. """
        tokens_dict = asdict(self)
        tokens_dict = { x: (y.isoformat() if isinstance(y, datetime) else y) for (x, y) in tokens_dict.items() }

        print(f"\nWriting token data to {filename}...")
        with open(filename, "w") as file:
            json.dump(tokens_dict, file, indent=4)
        print("Done.")

    @classmethod
    def read_session_id_from_json(cls, filename: str = SESSION_JSON) -> Self | None:
        """ Factory method:  reads session ID from a JSON file and instantiates a new `PelotonSessionIDToken`. """
        
        print(f"\nReading tokens from {filename}...\n")

        with open(filename, "r") as file:
            tokens_dict = json.load(file)
        session_id = tokens_dict['session_id']
        user_id = tokens_dict['user_id']
        created_at = datetime.fromisoformat(tokens_dict['created_at']).astimezone(tz=EASTERN_TIME)

        session_token = cls(session_id=session_id, 
                            user_id=user_id, 
                            created_at=created_at)
        return session_token


class PylotonZMV():
    def __init__(self, username: str = PELOTON_USERNAME, password: str = PELOTON_PASSWORD) -> None:
        self.username = username
        self.password = password
        self.session = requests.Session()

        try:
            self.login_token = PelotonSessionIDToken.read_session_id_from_json()
        except FileNotFoundError:
            print("JSON file not found.  Getting new login token...")
            self.get_new_login_token()
        except KeyError:
            print("Key error in JSON file.  Getting new login token...")
            self.get_new_login_token()
        else:
            self.session.cookies.set('peloton_session_id', self.login_token.session_id)

        self.total_workouts = None
        self.instructor_id_dict = {}  # Dictionary for caching Instructor IDs
        self.tried_once_already = False

    def get_new_login_token(self) -> None:
        print("Getting new session ID and resuming in 3 seconds...")
        time.sleep(3)
        auth_login_url = f"{BASE_URL}/auth/login"
        auth_payload = {'username_or_email': self.username, 'password': self.password}
        headers = {'Content-Type': 'application/json', 'User-Agent': 'pyloton'}
        resp = self.session.post(url=auth_login_url,json=auth_payload, headers=headers, timeout=10)
        resp.raise_for_status()
        
        self.login_token = PelotonSessionIDToken(resp.json()['session_id'], resp.json()['user_id'])
        self.login_token.write_session_id_json()
        self.session.cookies.set('peloton_session_id', self.login_token.session_id)

    def get_user_id(self) -> str:
        try:
            resp = self.session.get(f"{BASE_URL}/api/me", timeout=10)
            resp.raise_for_status()
            return resp.json()["id"]
        except requests.HTTPError:
            self.get_new_login_token()
            resp = self.session.get(f"{BASE_URL}/api/me", timeout=10)
            resp.raise_for_status()
            return resp.json()["id"]

    def get_total_workouts(self) -> int:
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
        if num_workouts is None:
            num_workouts = (self.get_total_workouts() if self.total_workouts is None 
                                                    else self.total_workouts)

        limit = min(100, num_workouts)
        pages = (1 if limit < 100 
                   else ((num_workouts // limit) + min(1, (num_workouts % limit))))
           
        base_workout_url = f"{BASE_URL}/api/user/{self.login_token.user_id}/workouts?sort_by=-created"
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

    def get_workout_summary_by_id(self, workout_id: str):
        url = f"{BASE_URL}/api/workout/{workout_id}"
        try:
            resp = self.session.get(url, timeout=10)
            resp.raise_for_status()
        except requests.HTTPError:
            self.get_new_login_token()
            resp = self.session.get(url, timeout=10)
            resp.raise_for_status()
            
        return resp.json()

    def get_workout_metrics_by_id(self, workout_id: str, frequency: int = 60):
        url = f"{BASE_URL}/api/workout/{workout_id}/performance_graph?every_n={frequency}"
        try:
            resp = self.session.get(url, timeout=10)
            resp.raise_for_status()
        except requests.HTTPError:
            self.get_new_login_token()
            resp = self.session.get(url, timeout=10)
            resp.raise_for_status()
            
        return resp.json()



def main():
    pass
    # token = PelotonSessionIDToken.read_session_id_from_json()#filename='asdfoihasf')
    # print(token)
    
    # pyloton = PylotonZMV()

    # print(f"Total Workouts: {pyloton.get_total_workouts()}")
    # # ids = pyloton.get_workout_ids(100)
    # # print(f"There are {len(ids)} Workout IDs: {ids}")
    # # pprint(pyloton.get_workout_summary_by_id('725f387569f049f497c2d53adebc1443'))
    # pprint(pyloton.get_workout_metrics_by_id('725f387569f049f497c2d53adebc1443'))

if __name__ == '__main__':
    main()