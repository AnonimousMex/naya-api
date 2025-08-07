from uuid import UUID

from sqlmodel import Session, func, join, select
from sqlalchemy.orm import selectinload
from app.api.emotions.emotion_model import AnswerModel, EmotionModel, EmotionResultsModel, StoryModel, TestAnswerModel
from app.api.test.questions_model import QuestionModel
from app.api.test.test_model import TestModel
from app.core.http_response import NayaHttpResponse
from app.models.user_model import UserModel


class TestService:
    @staticmethod
    async def create_test(session: Session, user_id: UUID ):
        try:
            new_test = TestModel(user_id=user_id)
            session.add(new_test)
            session.commit()
            session.refresh(new_test)
            return new_test.id
        except Exception:
            NayaHttpResponse.internal_error()

    @staticmethod
    async def get_stories(
        session
    ):
        try:
            subq_emotions = (
                select(StoryModel.emotion_id)
                .distinct()
                .order_by(StoryModel.emotion_id) 
                .limit(5)
            ).alias("distinct_emotions")

          # Para cada emoción, obtener una situación aleatoria
            subq_random_situations = (
                select(StoryModel)
                .join(
                    subq_emotions,
                    StoryModel.emotion_id == subq_emotions.c.emotion_id
                )
                .order_by(func.random())  
                .limit(5)
            ).alias("random_situations")

            query = (
                select(StoryModel)
                .select_from(subq_random_situations)
                .join(
                    StoryModel,
                    StoryModel.id == subq_random_situations.c.id
                )
                .options(selectinload(StoryModel.emotion))
            )
            situations = session.exec(query).all()
            result = []
            for situation in situations:
                
                question_query = (
                    select(QuestionModel.id, QuestionModel.question)
                    .where(QuestionModel.story_id == situation.id)
                )
                question = session.exec(question_query).first()

                answers_query = (
                    select(AnswerModel.id, AnswerModel.answer_text)
                    .where(AnswerModel.question_id == question.id)
                )

                answers =  session.exec(answers_query).all()
                # Construir el objeto de respuesta
                situation_dict = {
                    "id": situation.id,
                    "title": situation.title,
                    "story": situation.stage_1,
                    "question_id": question.id,
                    "question": question.question,
                    "answers": [
                        {
                            "id": answer.id,
                            "name": answer.answer_text,
                        } for answer in answers
                    ]
                }
                result.append(situation_dict)
            return result
        except Exception as e:
            NayaHttpResponse.internal_error()
        
    @staticmethod
    async def relation_answer_test(session: Session, answer_id: UUID, test_id: UUID):
        try:
            relation = TestAnswerModel(answer_id=answer_id, test_id=test_id)
            session.add(relation)
            session.commit()
            session.refresh(relation)
            return 
        except Exception:
            NayaHttpResponse.internal_error()

    @staticmethod
    async def exist_relation_answer_test(session: Session, answer_id: UUID, test_id: UUID):
        try:
            statement = (
                select(TestAnswerModel)
                .where(TestAnswerModel.answer_id == answer_id, TestAnswerModel.test_id == test_id)
            )
            exist = session.exec(statement).first()
            return exist if exist else False
        except Exception as e:
            NayaHttpResponse.internal_error()
    @staticmethod
    async def is_test_complete(session: Session, test_id: UUID):
        try:
            statement = (
                select(func.count())
                .where(TestAnswerModel.test_id == test_id)
                .select_from(TestAnswerModel)
            )
            count_answers = session.scalar(statement)
            return count_answers
        except Exception :
            NayaHttpResponse.internal_error()
        
    @staticmethod
    async def list_answers(session: Session, test_id: UUID):
        try:
            statement = (
                select(TestAnswerModel)
                .where(TestAnswerModel.test_id == test_id)
            )
            answers = session.exec(statement).all()
            result = []
            for answer in answers:
                answer_info = (
                    select(AnswerModel.answer_text, StoryModel.stage_1)
                    .where(AnswerModel.id == answer.answer_id)
                    .join(QuestionModel, QuestionModel.id == AnswerModel.question_id)
                    .join(StoryModel, StoryModel.id == QuestionModel.story_id)
                )
                query_answer_info= session.exec(answer_info).first()
                if query_answer_info:
                    answer_text, story_text = query_answer_info

                answers_dict = {
                    "story": story_text,
                    "answer": answer_text
                }

                result.append(answers_dict)
            return result
        except Exception as e:
            raise e
        
    @staticmethod
    async def test_details(session: Session, test_id: UUID, user_id: UUID):
        try:
            statement = (
                select(TestModel.created_at, UserModel.name)
                .where(TestModel.id == test_id, TestModel.user_id == user_id)
                .join(UserModel, UserModel.id == TestModel.user_id)
            )
            test_details = session.exec(statement).first()
            created_at, patient_name = test_details
            month_names = {
                1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
                5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
                9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
            }
            formatted_date = f"{created_at.day}/{month_names[created_at.month]}/{created_at.year}"
            return {
                "date": formatted_date,
                "name": patient_name
            }
        except Exception as e:
            raise e
    
    @staticmethod
    async def create_answer_details(session: Session, test_id: UUID):
        try:
            count_typeanswers = (
                select(AnswerModel.emotion_id, EmotionModel.name, func.count().label("total"))
                .where(TestAnswerModel.test_id == test_id)
                .select_from(TestAnswerModel)
                .join(AnswerModel, AnswerModel.id == TestAnswerModel.answer_id)
                .join(EmotionModel, EmotionModel.id == AnswerModel.emotion_id)
                .group_by(AnswerModel.emotion_id, EmotionModel.name)
            )
            answers = session.exec(count_typeanswers).all()
            result = []
            for answer in answers:
                percentage = answer.total * 20.0
                result = EmotionResultsModel(test_id=test_id, emotion_id=answer.emotion_id, percentage=percentage)
                session.add(result)
                session.commit()
                session.refresh(result)
            return answers 
        # Retorno la cantitdad de cada respuest y emocion posible reutilizacion de codigo para 
        #   falta el hacer en porcentaje de cada una de ellas
        except Exception as e:
            raise e
        
    @staticmethod
    async def get_percentage_results(session: Session, test_id: UUID):
        try:
            results = session.exec(
                select(EmotionResultsModel.emotion_id, EmotionModel.name, EmotionResultsModel.percentage)
                .where(EmotionResultsModel.test_id == test_id)
                .join(EmotionModel, EmotionModel.id == EmotionResultsModel.emotion_id)
                ).all()
            return results if results else False
        except Exception as e:
            raise e