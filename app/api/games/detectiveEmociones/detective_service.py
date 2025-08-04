import random
from sqlmodel import select, func
from sqlalchemy.orm import selectinload
from app.api.emotions.emotion_model import EmotionModel, SituationModel


class DetectiveService:
    @staticmethod
    async def get_situations(
        session
    ):
        try:
            subq_emotions = (
                select(SituationModel.emotion_id)
                .distinct()
                .order_by(SituationModel.emotion_id) 
                .limit(4)
            ).alias("distinct_emotions")

          # Para cada emoción, obtener una situación aleatoria
            subq_random_situations = (
                select(SituationModel)
                .join(
                    subq_emotions,
                    SituationModel.emotion_id == subq_emotions.c.emotion_id
                )
                .order_by(func.random())  
                .limit(4)
            ).alias("random_situations")

            query = (
                select(SituationModel)
                .select_from(subq_random_situations)
                .join(
                    SituationModel,
                    SituationModel.id == subq_random_situations.c.id
                )
                .options(selectinload(SituationModel.emotion))
            )
            situations = session.exec(query).all()
            result = []
            for situation in situations:
                correct_emotion = session.exec(
                    select(EmotionModel)
                    .where(EmotionModel.id == situation.emotion_id)
                ).first()
                # Obtener 3 emociones distintas (excluyendo la de la situación actual)
                options_query = session.exec(
                    select(EmotionModel)
                    .where(EmotionModel.id != situation.emotion_id)
                    .order_by(func.random())
                    .limit(3)
                ).all()

                all_options = [
                    {"id": correct_emotion.id, "name": correct_emotion.name, "isCorrect": True}
                ] + [
                    {"id": emotion.id, "name": emotion.name, "isCorrect": False} 
                    for emotion in options_query
                ]
                random.shuffle(all_options)
                
                # Construir el objeto de respuesta
                situation_dict = {
                    "id": situation.id,
                    "title": situation.title,
                    "story": situation.story,
                    "options": all_options
                }
                result.append(situation_dict)
            return result
        except Exception as e:
            
            raise e 