import json
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
from pprint import pprint
from pydantic import ValidationError

import requests
from constants import PELOTON_PASSWORD, PELOTON_USERNAME
from typing_extensions import Self
from pyloton_models import PelotonInstructor
from pyloton_connector import PylotonZMVConnector

BASE_URL = "https://api.onepeloton.com"
EASTERN_TIME = ZoneInfo('America/New_York')
INSTRUCTORS_JSON = Path('..').resolve().joinpath('peloton_instructors.json')

class PelotonInstructorNotFoundError(Exception):
    pass

class PelotonInstructorFinder():
    def __init__(self, pyloton: PylotonZMVConnector = None, 
                 username: str = PELOTON_USERNAME, password: str = PELOTON_PASSWORD) -> None:
        if pyloton is None:
            self.pyloton = PylotonZMVConnector(username, password)
        else:
            self.pyloton = pyloton
        self.instructors_dict = self.get_instructors_dict()

    def get_instructors_dict(self) -> dict:
        try:
            with open(INSTRUCTORS_JSON, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return dict()

    def export_instructor_id_dict_to_json(self) -> None:
        with open(INSTRUCTORS_JSON, 'w') as f:
            json.dump(self.instructors_dict, f)

    def get_instructor_by_id(self, instructor_id: str):
        if instructor_id in self.instructors_dict.keys():
            print(f"Found {self.instructors_dict[instructor_id]['full_name']} in dictionary!")
            return self.instructors_dict[instructor_id]

        url = f"{BASE_URL}/api/instructor/{instructor_id}"
        try:
            resp = self.pyloton.session.get(url, timeout=10)
            resp.raise_for_status()
        except requests.HTTPError:
            if resp.status_code == 401:
                self.pyloton.get_new_login_token()
                resp = self.pyloton.session.get(url, timeout=10)
                resp.raise_for_status()
            elif resp.status_code == 404:
                raise PelotonInstructorNotFoundError(
                    f"Instructor ID '{instructor_id}' not found.")
        try:
            instructor = PelotonInstructor.model_validate(resp.json())
            self.instructors_dict.update({instructor_id: instructor.model_dump()})
            self.export_instructor_id_dict_to_json()
            return instructor
        except ValidationError as e:
            print(e)
            return None

def main():
    finder = PelotonInstructorFinder()
    
    # print(finder.instructors_dict)
    # print(finder.get_instructor_by_id('561f95c405734d8488ed8dcc8980d599'))
    # print(finder.get_instructor_by_id('c0a9505d8135412d824cf3c97406179b'))
    print(finder.get_instructor_by_id('048f0ce00edb4427b2dced6cbeb107fd'))

if __name__ == '__main__':
    main()