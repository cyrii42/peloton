import json
import time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
from pprint import pprint

import requests
from constants import PELOTON_PASSWORD, PELOTON_USERNAME
from pyloton_connector import PylotonZMVConnector

BASE_URL = "https://api.onepeloton.com"
EASTERN_TIME = ZoneInfo('America/New_York')
INSTRUCTORS_JSON = Path('..').resolve().joinpath('peloton_instructors.json')



class PylotonZMV():
    def __init__(self, username: str = PELOTON_USERNAME, password: str = PELOTON_PASSWORD) -> None:
        self.pyloton = PylotonZMVConnector(username, password)
        self.total_workouts = None

    def get_total_workouts(self) -> int:
        try:
            resp = self.pyloton.session.get(f"{BASE_URL}/api/me", timeout=10)
            resp.raise_for_status()
            return resp.json()["total_workouts"]
        except requests.HTTPError:
            self.pyloton.get_new_login_token()
            resp = self.pyloton.session.get(f"{BASE_URL}/api/me", timeout=10)
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
                resp = self.pyloton.session.get(url, timeout=10)
                resp.raise_for_status()
            except requests.HTTPError:
                self.pyloton.get_new_login_token()
                resp = self.pyloton.session.get(url, timeout=10)
                resp.raise_for_status()
                
            for dataset in resp.json()['data']:
                workout_id_list.append(dataset['id'])

        return workout_id_list

    def get_workout_summary_by_id(self, workout_id: str):
        url = f"{BASE_URL}/api/workout/{workout_id}"
        try:
            resp = self.pyloton.session.get(url, timeout=10)
            resp.raise_for_status()
        except requests.HTTPError:
            self.pyloton.get_new_login_token()
            resp = self.pyloton.session.get(url, timeout=10)
            resp.raise_for_status()
            
        output_dict = resp.json()
        output_dict.update({'workout_id': workout_id}) 
        return output_dict

    def get_workout_metrics_by_id(self, workout_id: str, frequency: int = 60):
        url = f"{BASE_URL}/api/workout/{workout_id}/performance_graph?every_n={frequency}"
        try:
            resp = self.pyloton.session.get(url, timeout=10)
            resp.raise_for_status()
        except requests.HTTPError:
            self.pyloton.get_new_login_token()
            resp = self.pyloton.session.get(url, timeout=10)
            resp.raise_for_status()
            
        output_dict = resp.json()
        output_dict.update({'workout_id': workout_id}) 
        return output_dict

    def get_user_id(self) -> str:
        try:
            resp = self.pyloton.session.get(f"{BASE_URL}/api/me", timeout=10)
            resp.raise_for_status()
            return resp.json()["id"]
        except requests.HTTPError:
            self.pyloton.get_new_login_token()
            resp = self.pyloton.session.get(f"{BASE_URL}/api/me", timeout=10)
            resp.raise_for_status()
            return resp.json()["id"]



def main():
    pass
    # token = PelotonSessionIDToken.read_session_id_from_json()#filename='asdfoihasf')
    # print(token)
    
    pyloton = PylotonZMV()
    
    # print(pyloton.instructors_dict)
    # print(pyloton.get_instructor_full_name_by_id('561f95c405734d8488ed8dcc8980d599'))
    # print(pyloton.get_instructor_full_name_by_id('c0a9505d8135412d824cf3c97406179b'))
    print(pyloton.get_instructor_full_name_by_id('048f0ce00edb4427b2dced6cbeb107fd'))
    # pyloton.export_instructor_id_dict_to_json()
    # json_output = instructor1.model_dump_json(indent=2)
    # with open('test.json', 'w') as f:
    #     json.dump(pyloton.instructor_id_dict.model_dump_json(indent=2), f)
    

    # print(f"Total Workouts: {pyloton.get_total_workouts()}")
    # # ids = pyloton.get_workout_ids(100)
    # # print(f"There are {len(ids)} Workout IDs: {ids}")
    # # pprint(pyloton.get_workout_summary_by_id('725f387569f049f497c2d53adebc1443'))
    # pprint(pyloton.get_workout_metrics_by_id('725f387569f049f497c2d53adebc1443'))

if __name__ == '__main__':
    main()