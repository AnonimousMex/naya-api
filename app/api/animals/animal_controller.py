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
        # Consulta equivalente a la SQL proporcionada
        rows = self.session.exec(
            select(
                AnimalModel.id,
                AnimalModel.name,
                AnimalModel.description,
                AnimalModel.color_ui,
                PictureModel.picture,
                PictureAnimalEmotionModel.id_emotion
            )
            .join(PictureAnimalEmotionModel, PictureAnimalEmotionModel.id_animal == AnimalModel.id)
            .join(PictureModel, PictureModel.id == PictureAnimalEmotionModel.id_picture)
            .where(PictureModel.is_profile == True)
        ).all()
        result = []
        for row in rows:
            animal_id = str(row[0])
            name = row[1]
            description = row[2]
            color_ui = row[3]
            default_profile_picture = str(row[4]) if row[4] is not None else None
            default_emotion_profile_picture = str(row[5]) if row[5] is not None else None
            result.append(AnimalResponseSchema(
                animal_id=animal_id,
                name=name,
                description=description,
                color_ui=color_ui,
                default_profile_picture=default_profile_picture,
                default_emotion_profile_picture=default_emotion_profile_picture
            ))
        return result
