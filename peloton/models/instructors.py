from pydantic import (AliasChoices, BaseModel, ConfigDict, Field,
                      computed_field, field_validator)
from typing import List, Optional


class PelotonHumanInstructor(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)
    instructor_id: str = Field(alias=AliasChoices('ride_instructor_id', 'id'))
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
    life_style_image_url: Optional[str] = None
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
