from app.api.animals.animal_model import AnimalModel
from app.api.pictures.picture_animal_emotion_model import PictureAnimalEmotionModel
from app.api.pictures.picture_model import PictureModel
from sqlmodel import select
from .animal_schema import AnimalResponseSchema
from typing import List

class AnimalController:
    def __init__(self, session):
        self.session = session

    async def list_animals(self) -> List[AnimalResponseSchema]:
        animals = self.session.exec(select(AnimalModel)).all()
        result = []
        for animal in animals:
            happy_picture = (
                self.session.exec(
                    select(PictureModel.picture)
                    .join(PictureAnimalEmotionModel, PictureAnimalEmotionModel.id_picture == PictureModel.id)
                    .where(
                        PictureAnimalEmotionModel.id_animal == animal.id,
                        PictureModel.is_profile == True
                    )
                ).first()
            )
            result.append(AnimalResponseSchema(
                id=str(animal.id),
                name=animal.name,
                description=animal.description,
                color_ui=animal.color_ui,
                happy_profile_picture=happy_picture[0] if happy_picture else None
            ))
        return result
