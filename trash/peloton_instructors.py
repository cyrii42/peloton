
import json
from pathlib import Path
from pprint import pprint
from zoneinfo import ZoneInfo

import requests
from peloton_exceptions import PelotonInstructorNotFoundError
from pydantic import (AliasChoices, BaseModel, ConfigDict, Field,
                      ValidationError, computed_field, field_validator)
from pyloton_connector import PylotonZMVConnector
import peloton_json
from typing_extensions import List

BASE_URL = "https://api.onepeloton.com"
EASTERN_TIME = ZoneInfo('America/New_York')
INSTRUCTORS_JSON = Path('..').resolve().joinpath('peloton_instructors.json')
WORKOUTS_DIR = Path('..').resolve().joinpath('data', 'workouts')


class PelotonHumanInstructor(BaseModel):
    model_config = ConfigDict(frozen=True)
    instructor_id: str = Field(alias=AliasChoices('ride_instructor_id', 'instructor_id', 'id'))
    first_name: str
    last_name: str
    about_image_url: str
    background: str
    bio: str
    fitness_disciplines: List[str]
    image_url: str
    instagram_profile: str
    instructor_hero_image_url: str
    ios_instructor_list_display_image_url: str
    jumbotron_url_dark: str
    jumbotron_url_ios: str
    life_style_image_url: str
    ordered_q_and_as: List[List[str]]
    quote: str
    short_bio: str
    spotify_playlist_uri: str
    strava_profile: str
    twitter_profile: str
    username: str
    web_instructor_list_display_image_url: str

    @computed_field
    def full_name(self) -> str:
        return self.first_name + ' ' + self.last_name

    @field_validator('instructor_id')
    @classmethod
    def instructor_id_is_UUID_not_all_zeroes(cls, instructor_id: str) -> str:
        if instructor_id is None or len(instructor_id) != 32 or instructor_id.count('0') == 32:
            return None
        else:
            return instructor_id

class PelotonNonHumanInstructor(BaseModel):
    ''' With human instructors, the `instructor` field is empty in the `ride` column, but with 
    "JUST RIDE" or "LANEBREAK" or "ENTERTAINMENT" rides, it's not:
    
    `'instructor': {'name': 'JUST RIDE',
    'image_url': 'https://s3.amazonaws.com/peloton-ride-images/just-ride-indoor.png'}`'''
    
    name: str
    image_url: str

def get_instructor_by_id(instructor_id: str) -> PelotonHumanInstructor | None:
    json_writer = peloton_json.PelotonJSONWriter()
    instructors_dict = json_writer.get_instructors_dict_from_json()
        
    if instructor_id in instructors_dict.keys():
        return PelotonHumanInstructor.model_validate(instructors_dict[instructor_id])
    
    else:
        url = f"{BASE_URL}/api/instructor/{instructor_id}"
        try:
            py_conn = PylotonZMVConnector()
            resp = py_conn.session.get(url, timeout=10)
            resp.raise_for_status()
        except requests.HTTPError:
            if resp.status_code == 401:
                py_conn.get_new_login_token()
                resp = py_conn.session.get(url, timeout=10)
                resp.raise_for_status()
            elif resp.status_code == 404:
                raise PelotonInstructorNotFoundError(f"Instructor ID '{instructor_id}' not found.")
            else:
                raise requests.HTTPError
            
        try:
            instructor = PelotonHumanInstructor.model_validate(resp.json())
            json_writer.add_instructor_to_json(instructor.model_dump())
            return instructor
        except ValidationError as e:
            print(e)
            return None