from sqlmodel import Session, select, func, text
from sqlalchemy.orm import aliased, selectinload
from sqlalchemy import literal_column
from sqlalchemy.sql import over
from app.api.emotions.emotion_model import SituationModel
from app.api.games.memociones.memociones_schema import MemocionPairResponse


class MemocionService:
    @staticmethod
    def get_emotion_situation_pairs(session: Session) -> list[MemocionPairResponse]:
        from sqlalchemy import func

        row_number = (
            func.row_number()
            .over(partition_by=SituationModel.emotion_id, order_by=func.random())
            .label("rn")
        )

        stmt = (
            select(SituationModel, row_number)
            .options(selectinload(SituationModel.emotion))
            .subquery()
        )

        aliased_situation = aliased(SituationModel, stmt)

        query = select(aliased_situation).where(stmt.c.rn == 1).limit(6)

        results = session.exec(query).all()

        return [
            MemocionPairResponse(
                pair_id=situation.id,
                emotion=situation.emotion.name.title(),
                situation=situation.story,
            )
            for situation in results
        ]
