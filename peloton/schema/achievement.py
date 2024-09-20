from pydantic import BaseModel, ConfigDict, Field, AliasChoices
    
class PelotonAchievement(BaseModel):
    model_config = ConfigDict(frozen=True)
    achievement_id: str = Field(alias=AliasChoices('id', 'achievement_id', 'workout_id'))
    name: str
    slug: str
    image_url: str = Field(repr=False)
    description: str
    achievement_count: int