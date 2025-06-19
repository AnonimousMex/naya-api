
from fastapi import APIRouter
from sqlmodel import Session

from .patient_schema import PatientCreateSchema, PatientResponseSchema
from app.core.http_response import NayaResponseModel


patients_router = APIRouter()

@patients_router.post(
    "/patients",
     response_model=NayaResponseModel[PatientResponseSchema],
)
async def create_patient(patient_data: PatientCreateSchema, session: Session):
    pass

##Agregar lo de mindfultoc