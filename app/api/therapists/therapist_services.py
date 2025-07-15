from sqlmodel import Session, select
from app.api.therapists.therapist_model import TherapistModel, AppointmentModel
from uuid import UUID
from sqlmodel import Session, select
from app.api.auth.auth_model import ConnectionModel
from app.api.therapists.therapist_model import TherapistModel
from app.models.user_model import UserModel
from app.constants.response_codes import NayaResponseCodes
from app.core.http_response import NayaHttpResponse
from uuid import UUID
from datetime import date, time, datetime, timezone
from app.api.therapists.therapist_schema import AppointmentListResponse
from app.api.therapists.therapist_schema import TherapistListResponseSchema
from app.api.patients.patient_model import PatientModel
from app.api.patients.patient_schema import ListPatientResponseSchema
from typing import List



class TherapistService:

    @staticmethod
    async def get_therapist_by_id(
        therapist_id: UUID, session: Session
    ) -> TherapistModel | None:
        stmt = select(TherapistModel).where(TherapistModel.id == therapist_id)
        return session.exec(stmt).first()

    @staticmethod
    async def create_therapist(user: UserModel, session: Session) -> TherapistModel:
        try:
            new_therapist = TherapistModel(user=user, user_id=user.id)

            session.add(new_therapist)
            session.commit()
            session.refresh(new_therapist)

            return new_therapist
        except Exception:
            NayaHttpResponse.internal_error()
    
    @staticmethod
    async def schedule_appointment(session: Session, therapist_id: UUID, patient_id: UUID, date: date, time: time ) -> AppointmentModel:
        try:
            new_appointment = AppointmentModel(therapist_id=therapist_id, patient_id=patient_id, date=date, time=time)

            session.add(new_appointment)
            session.commit()
            session.refresh(new_appointment)

            return new_appointment
        except Exception as e:
            raise NayaHttpResponse.internal_error()
        

    @staticmethod
    def appointment_exists(
        session: Session, *, therapist_id: UUID, date: date, time: time
    ) -> bool:
        stmt = select(AppointmentModel).where(
            AppointmentModel.therapist_id == therapist_id,
            AppointmentModel.date == date,
            AppointmentModel.time == time,
            AppointmentModel.status == True,
            AppointmentModel.deleted_at == None
        )
        return session.exec(stmt).first() is not None
    
    @staticmethod
    def cancel_appointment(
        session: Session, *, appointment_id: UUID
    ) -> bool:
        stmt = select(AppointmentModel).where(
            AppointmentModel.id == appointment_id
        )
        appointment = session.exec(stmt).first()
        appointment.status = False
        appointment.updated_at = datetime.now(timezone.utc)
        appointment.deleted_at = datetime.now(timezone.utc)
        session.add(appointment)
        session.commit()
        return appointment 

    @staticmethod
    async def list_appointments(
        session, therapist_id, patient_id
    ) -> list[AppointmentModel]:

        statement = select(AppointmentModel).where(AppointmentModel.therapist_id == therapist_id, AppointmentModel.patient_id==patient_id, AppointmentModel.deleted_at== None, AppointmentModel.status==True)
        results = session.exec(statement).all()
        response = [
            AppointmentListResponse(
                id=appointment.id,
                patient_id=appointment.patient_id,
                date=appointment.date,
                time=appointment.time,
            )
        for appointment in results
        ]
        return response    
    
    @staticmethod
    def reschedule_appointment(
        session: Session, *, appointment_id: UUID, date: date, time: time
    ) -> bool:
        stmt = select(AppointmentModel).where(
            AppointmentModel.id == appointment_id
        )
        appointment = session.exec(stmt).first()
        appointment.date = date,
        appointment.time = time,
        appointment.updated_at = datetime.now(timezone.utc)
        session.add(appointment)
        session.commit()
        return appointment 
    
    @staticmethod
    def complete_appointment(
        session: Session, *, appointment_id: UUID
    ) -> bool:
        stmt = select(AppointmentModel).where(
            AppointmentModel.id == appointment_id
        )
        appointment = session.exec(stmt).first()
        appointment.status = False
        appointment.updated_at = datetime.now(timezone.utc)
        session.add(appointment)
        session.commit()
        return appointment

    @staticmethod
    def delete_connection(session: Session, *, therapist_id: UUID, patient_id: UUID):
        stmt = select(ConnectionModel).where(
            ConnectionModel.therapist_id == therapist_id,
            ConnectionModel.patient_id == patient_id,
        )
        conn = session.exec(stmt).first()
        if conn:
            session.delete(conn)
            session.commit()

    @staticmethod
    async def list_verified_therapists(session) -> list:
        statement = (
            select(TherapistModel)
            .join(UserModel, TherapistModel.user_id == UserModel.id)
            .where(UserModel.is_verified == True)
        )
        results = session.exec(statement).all()
        if not results:
            NayaHttpResponse.not_found(
                data={
                    "message": NayaResponseCodes.NO_VERIFIED_THERAPISTS.detail,
                },
                error_id=NayaResponseCodes.NO_VERIFIED_THERAPISTS.code,
            )
        return [
            TherapistListResponseSchema(
                therapist_id=therapist.id,
                name=therapist.user.name
            )
            for therapist in results
        ]

    @staticmethod
    async def list_patients_by_therapist(
        therapist_id, session
    ) -> list[ListPatientResponseSchema]:
        statement = select(PatientModel).join(
            ConnectionModel, ConnectionModel.patient_id == PatientModel.id
        ).where(ConnectionModel.therapist_id == therapist_id)
        results = session.exec(statement).all()
        return [ListPatientResponseSchema(
            patient_id=patient.id,
            name=patient.user.name,
            animal_id=patient.animal_id
        ) for patient in results]
