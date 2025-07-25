from sqlmodel import select, func
from sqlalchemy.orm import selectinload
from app.api.emotions.emotion_model import SituationModel


class DetectiveSerivce:
    @staticmethod
    async def get_situations(
        session
    ):
        subq_emotions = (
            select(SituationModel.emotion_id)
            .distinct()
            .order_by(func.random())
            .limit(4) 
        ).subquery()

        subq_random_situations = (
            select(SituationModel)
            .where(SituationModel.emotion_id == subq_emotions.c.emotion_id)
            .order_by(func.random())
            .limit(1)
        ).lateral()  

        query = (
            select(SituationModel)
            .select_from(subq_emotions)
            .join(subq_random_situations, onclause=True)
            .options(selectinload(SituationModel.emotion))
        )