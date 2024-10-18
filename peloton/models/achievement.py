from pydantic import BaseModel, ConfigDict, Field, AliasChoices, computed_field
    
class PelotonAchievement(BaseModel):
    model_config = ConfigDict(frozen=True)
    achievement_id: str = Field(alias=AliasChoices('id', 'achievement_id', 'workout_id'))
    name: str
    slug: str
    image_url: str = Field(repr=False)
    description: str
    achievement_count: int

    @computed_field
    @property
    def image_local_filename(self) -> str | None:
        if self.image_url is None:
            return None
        else:
            return self.image_url.split(sep='/')[-1] + '.png'