from datetime import datetime
from typing import List
from uuid import UUID

from pydantic import BaseModel
from pydantic.alias_generators import to_camel


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
    emotion: str

class TestDetailsReponse(BaseModel):
    date: str
    total_answers: int
    patient_name: str

class EmotionPercentageResponse(BaseModel):
    emotion_id: UUID
    emotion_name: str
    percentage: float

class TestsResponse(BaseModel):
    id: UUID
    created_at: datetime
    user_id: UUID

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

class ListTestRequest (BaseModel):
    patient_id: UUID

    class config:
        alias_generator = to_camel
        populate_by_name = True

class TestDetailsRequest(BaseModel):
    test_id: UUID

    class config:
        alias_generator = to_camel
        populate_by_name = True