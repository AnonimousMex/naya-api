from app.api.animals.animal_model import AnimalModel
from sqlmodel import select
from .animal_schema import AnimalResponseSchema
from typing import List

class AnimalController:
    def __init__(self, session):
        self.session = session

    async def list_animals(self) -> List[AnimalResponseSchema]:
        rows = self.session.exec(
            select(
                AnimalModel.id,
                AnimalModel.name,
                AnimalModel.description,
                AnimalModel.color_ui,
                AnimalModel.animal_key
            )
        ).all()
        result = []
        for row in rows:
            animal_id = str(row[0])
            name = row[1]
            description = row[2]
            color_ui = row[3]
            animal_key = row[4]
            result.append(AnimalResponseSchema(
                animal_id=animal_id,
                name=name,
                description=description,
                color_ui=color_ui,
                animal_key=animal_key
            ))
        return result
