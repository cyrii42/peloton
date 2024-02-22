import json

from pydantic import (AliasChoices, BaseModel, ConfigDict, Field,
                      computed_field, field_validator, model_validator, ValidationInfo)
from typing import Optional, Any

from .instructors import PelotonHumanInstructor, PelotonNonHumanInstructor
from peloton.constants import INSTRUCTORS_JSON


class PelotonRideColumn(BaseModel):
    model_config = ConfigDict(frozen=True)
    title: Optional[str] = None
    description: Optional[str] = None
    ride_length: Optional[int] = Field(alias=AliasChoices('length', 'ride_length'), default=None)
    ride_duration: Optional[int] = Field(alias=AliasChoices('duration', 'ride_duration'), default=None)
    image_url: Optional[str] = None
    difficulty_estimate: Optional[float] = None
    fitness_discipline: Optional[str] = None
    ride_id: Optional[str] = Field(alias=AliasChoices('id', 'ride_id'), default=None)
    instructor_json: Optional[PelotonNonHumanInstructor] = Field(alias='instructor', default=None)
    instructor_id: Optional[str] = Field(alias=AliasChoices('instructor_id'), default=None)
        
    @field_validator('instructor_id')
    @classmethod
    def instructor_id_is_UUID_not_all_zeroes(cls, instructor_id: str) -> str:
        if instructor_id is None or len(instructor_id) != 32 or instructor_id.count('0') == 32:
            return None
        else:
            return instructor_id

    @field_validator('ride_duration')
    @classmethod
    def ride_duration_is_not_zero(cls, ride_duration: int, info: ValidationInfo) -> int:
        if ride_duration is not None and ride_duration > 0:
            return ride_duration
        elif info.data['ride_length'] is not None and info.data['ride_length'] > 0:
            return info.data['ride_length']
        else:
            return ride_duration

    @computed_field
    def instructor_name(self) -> str | None:
        if self.instructor_id is not None:
            try:
                with open(INSTRUCTORS_JSON, 'r') as f:
                    instructors_dict = json.load(f)
                if self.instructor_id in instructors_dict.keys():
                    instructor_data = instructors_dict[self.instructor_id]
                    instructor = PelotonHumanInstructor.model_validate(instructor_data)
                    return instructor.full_name
            except FileNotFoundError:
                print(f"File not found:  {INSTRUCTORS_JSON}")
                instructors_dict = dict()
                return None
        elif self.instructor_json is not None:
            return self.instructor_json.name
        else:
            return None

def main():
    print(INSTRUCTORS_JSON)

if __name__ == '__main__':
    main()