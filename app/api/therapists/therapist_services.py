
from sqlmodel import Session, select
from app.api.therapists.therapist_model import TherapistModel, AppointmentModel
from app.api.users.user_model import UserModel
from app.core.http_response import NayaHttpResponse
from uuid import UUID
from datetime import date, time, datetime, timezone
from app.api.therapists.therapist_schema import AppointmentListResponse



class TherapistService: 
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
        session: Session, *, id: UUID
    ) -> bool:
        stmt = select(AppointmentModel).where(
            AppointmentModel.id == id
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
        session: Session, *, id: UUID, date: date, time: time
    ) -> bool:
        stmt = select(AppointmentModel).where(
            AppointmentModel.id == id
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
        session: Session, *, id: UUID
    ) -> bool:
        stmt = select(AppointmentModel).where(
            AppointmentModel.id == id
        )
        appointment = session.exec(stmt).first()
        appointment.status = False
        appointment.updated_at = datetime.now(timezone.utc)
        session.add(appointment)
        session.commit()
        return appointment


