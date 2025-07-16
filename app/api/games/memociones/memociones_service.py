from sqlmodel import Session, func, select
from sqlalchemy.orm import selectinload
from app.api.emotions.emotion_model import SituationModel
from app.api.games.memociones.memociones_schema import MemocionPairResponse


class MemocionService:
    @staticmethod
    def get_emotion_situation_pairs(session: Session) -> list[MemocionPairResponse]:
        stmt = (
            select(SituationModel)
            .options(selectinload(SituationModel.emotion))
            .order_by(func.random())  # orden aleatorio
            .limit(6)  # máximo 6 resultados
        )
        situations = session.exec(stmt).all()

        return [
            MemocionPairResponse(
                pair_id=situation.id,
                emotion=situation.emotion.name.title(),
                situation=situation.story,
            )
            for situation in situations
        ]
