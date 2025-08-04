from sqlmodel import select, Session
from app.api.games.y_ese_ruido.y_ese_ruido_schema import GameSoundsResponse
from app.api.games.y_ese_ruido.y_ese_ruido_model import SoundsGameCluesModel, SoundsGameSoundsModel
from app.api.emotions.emotion_model import EmotionModel
from sqlalchemy.sql.expression import func


class YEseRuidoService:
    @staticmethod
    def get_sounds(session: Session) -> list[GameSoundsResponse]:
      
        statement = (
            select(SoundsGameCluesModel, SoundsGameSoundsModel, EmotionModel)
            .join(SoundsGameSoundsModel, SoundsGameCluesModel.sound_id == SoundsGameSoundsModel.id)
            .join(EmotionModel, SoundsGameSoundsModel.emotion_id == EmotionModel.id)
            .order_by(func.random()) 
            .limit(4)                
        )

        try:
            results = session.exec(statement).all()
            
        except Exception as e:
            raise

        try:
            response = [
                GameSoundsResponse(
                    audio_path=sound.audio_path,
                    emotion=emotion.name,
                    title=clue.title,
                    body=clue.body,
                    tip=clue.tip,
                    highlight=clue.highlight
                )
                for clue, sound, emotion in results
            ]
            return response
        except Exception as e:
            raise