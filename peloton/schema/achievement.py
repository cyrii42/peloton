from pydantic import BaseModel, ConfigDict, Field, AliasChoices, field_validator
    
class PelotonAchievement(BaseModel):
    model_config = ConfigDict(frozen=True)
    workout_id: str = Field(alias=AliasChoices('id', 'workout_id'))
    name: str
    slug: str
    image_url: str
    description: str
    achievement_count: int
    
    @field_validator('workout_id')
    @classmethod
    def workout_id_is_UUID_not_all_zeroes(cls, workout_id: str) -> str:
        if workout_id is None or len(workout_id) != 32 or workout_id.count('0') == 32:
            raise ValueError("invalid Workout ID")
        else:
            return workout_id