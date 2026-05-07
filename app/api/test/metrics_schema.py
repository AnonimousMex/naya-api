"""Schemas Pydantic para activity-results y métricas."""
from datetime import date, datetime
from typing import Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class AnswerInput(BaseModel):
    question_id: UUID
    answer_id: UUID
    emotion_intensity: Optional[int] = Field(default=None, ge=0, le=100)
    coping_category: Optional[str] = None  # avoidance | frustration | abandonment


class ActivityResultCreate(BaseModel):
    child_id: UUID
    activity_id: Optional[UUID] = None
    duration_seconds: Optional[int] = Field(default=None, ge=0)
    score: Optional[int] = Field(default=None, ge=0, le=100)
    completed_at: Optional[datetime] = None
    answers: List[AnswerInput] = Field(default_factory=list)


class ActivityResultCreated(BaseModel):
    test_id: UUID
    child_id: UUID
    answers_recorded: int


class AnswersBatch(BaseModel):
    """Cuerpo del POST /activity-results/{test_id}/answers."""
    answers: List[AnswerInput] = Field(default_factory=list)


class AnswersBatchResult(BaseModel):
    test_id: UUID
    answers_recorded: int
    total_answers: int


class ActivityResultUpdate(BaseModel):
    """Cuerpo del PATCH /activity-results/{test_id}. Todos los campos opcionales."""
    score: Optional[int] = Field(default=None, ge=0, le=100)
    duration_seconds: Optional[int] = Field(default=None, ge=0)
    completed_at: Optional[datetime] = None
    activity_id: Optional[UUID] = None


class ActivityResultAnswerDetail(BaseModel):
    answer_id: UUID
    question_id: Optional[UUID] = None
    answer_text: Optional[str] = None
    emotion: Optional[str] = None
    emotion_intensity: Optional[int] = None
    coping_category: Optional[str] = None


class ActivityResultDetail(BaseModel):
    test_id: UUID
    child_id: UUID
    activity_id: Optional[UUID] = None
    score: Optional[int] = None
    duration_seconds: Optional[int] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    is_complete: bool
    answers: List[ActivityResultAnswerDetail]


class Period(BaseModel):
    start: date
    end: date


class TherapistTrend(BaseModel):
    title: str
    description: str
    clinical_note: str


class TherapistMetricsResponse(BaseModel):
    child_id: str
    period: Period
    answers_count: int
    emotional_statistics: Dict[str, int]
    coping_statistics: Dict[str, int]
    emotional_triggers: Dict[str, int]
    frequent_answers: List[str]
    weekly_evolution: List[Dict]
    trend: TherapistTrend
    disclaimer: str


class TutorSummary(BaseModel):
    main_emotion: str
    main_emotion_percentage: int
    completed_activities: int
    progress_status: str


class TutorTrend(BaseModel):
    title: str
    description: str


class TutorProgressResponse(BaseModel):
    child_id: str
    period: Period
    summary: TutorSummary
    emotional_progress: Dict[str, int]
    child_trend: TutorTrend
    recommendation: str
    frequent_phrases: List[str]
    disclaimer: str


class ActivityHistoryItem(BaseModel):
    test_id: str
    activity_id: Optional[str]
    date: str
    score: Optional[int]
    duration_seconds: Optional[int]
    main_emotion: Optional[str]
