from datetime import datetime
from typing import List
from uuid import UUID

from pydantic import BaseModel
from pydantic.alias_generators import to_camel
from sqlmodel import Double


class AnswersList(BaseModel):
    id: UUID
    name: str

class StoriesResponse(BaseModel):
    id: UUID
    title: str
    story: str
    image_url: str
    question_id: UUID
    question: str
    answers: List[AnswersList]

class TestStoriesResponse(BaseModel):
    test_id:  UUID
    stories: List[StoriesResponse]

class AnswersResponse(BaseModel):
    story: str
    answer: str

class TestDetailsReponse(BaseModel):
    date: str
    total_answers: int
    patient_name: str

class EmotionPercentageResponse(BaseModel):
    emotion_id: UUID
    emotion_name: str
    percentage: float



class PostAnswerRequest(BaseModel):
    test_id: UUID
    answer_id: UUID

    class config:
        alias_generator = to_camel
        populate_by_name = True

class AnswersRequest(BaseModel):
    test_id: UUID

    class config:
        alias_generator = to_camel
        populate_by_name = True

class TestDetailsRequest(BaseModel):
    patient_id: UUID
    test_id: UUID

    class config:
        alias_generator = to_camel
        populate_by_name = True