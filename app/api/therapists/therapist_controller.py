from uuid import UUID

from fastapi import HTTPException

from sqlmodel import Session
from datetime import date, time

from app.api.auth.auth_service import AuthService
from app.api.therapists.therapist_services import TherapistService
from app.constants.response_codes import NayaResponseCodes
from app.core.http_response import NayaHttpResponse

from app.constants.user_constants import UserRoles, VerificationModels

from app.api.users.user_service import UserService
from app.api.users.user_controller import UserController
from app.api.users.user_schema import UserCreateSchema, UserResponseSchema
from app.utils.email import EmailService
from app.utils.security import decode_token
from fastapi.encoders import jsonable_encoder


from .therapist_schema import TherapistResponseSchema, TherapistCreateSchema, AppointmentRequest, AppointmentResponse


class TherapistController:
    def __init__(self, session: Session):
        self.session = session

    async def create_therapist(
        self, therapist_data: TherapistCreateSchema
    ) -> TherapistResponseSchema:
        try:
            user_controller = UserController(session=self.session)

            await user_controller.validate_exixting_user(
                user_email=therapist_data.email
            )

            # We should do a stronger validation if schemas change (UserCreateSchema and PatientCreateSchema)
            user_data: UserCreateSchema = therapist_data

            user = await UserService.create_user(
                user_data=user_data, user_kind=UserRoles.THERAPIST, session=self.session
            )

            therapist = await TherapistService.create_therapist(
                user=user, session=self.session
            )

            new_verification_code = await AuthService.generate_unique_verification_code(
                session=self.session, model=VerificationModels.VERIFICATION_CODE_MODEL
            )

            verification_code = await AuthService.create_verification_code(
                code=new_verification_code, user_id=user.id, session=self.session
            )
            
            await EmailService.send_verification_email(
                to_name=user.name.capitalize(),
                to_email=user.email,
                verification_code=verification_code.code,
            )

            new_conection_code = await AuthService.generate_unique_conection_code(
                session=self.session
            )

            conection_code = await AuthService.create_conection_code(
                code=new_conection_code, user_id=user.id, session=self.session
            )

            await EmailService.send_conection_code_email(
                to_name=user.name.capitalize(),
                to_email=user.email,
                verification_code=conection_code,
            )
            
            user_dump = UserResponseSchema.model_validate(user).model_dump()

            response = TherapistResponseSchema(**user_dump, therapist_id=therapist.id)

            return response

        except HTTPException as e:
            raise e

        except Exception:
            NayaHttpResponse.internal_error()

    async def get_therapist_by_id(self, therapist_id: UUID) -> TherapistResponseSchema:
        try:
            therapist = await TherapistService.get_therapist_by_id(
                therapist_id=therapist_id, session=self.session
            )

            if therapist is None:
                NayaHttpResponse.not_found(
                    data={
                        "message": NayaResponseCodes.UNEXISTING_THERAPIST.detail,
                        "providedValue": str(therapist_id),
                    },
                    error_id=NayaResponseCodes.UNEXISTING_THERAPIST.code,
                )

            user_dump = UserResponseSchema.model_validate(therapist.user).model_dump()

            response = TherapistResponseSchema(**user_dump, therapist_id=therapist_id)

            return response

        except HTTPException as e:
            raise e

        except Exception:
            NayaHttpResponse.internal_error()

    async def create_appointment(
        self, token: str, patient_id: UUID, date: date, time: time 
    ) -> AppointmentResponse:
        try:
            decoded = decode_token(token)
          
            if decoded:
                user_id = decoded.get("sub")
            
            therapist = AuthService.get_therapist_by_user_id(self.session, user_id=user_id)

            if TherapistService.appointment_exists(
            self.session, therapist_id=therapist.id, date= date, time=time
            ):
                NayaHttpResponse.bad_request(
                data={
                    "message": NayaResponseCodes.APPOINTMENT_EXISTS.detail,
                    "providedValue": {
                        "therapist_id": str(therapist.id),
                        "patient_id": str(patient_id),
                        "date": str(date),
                        "time": str(time)
                    },
                },
                error_id=NayaResponseCodes.APPOINTMENT_EXISTS.code,
            )
            appointment = await TherapistService.schedule_appointment(
                self.session, therapist_id=therapist.id , patient_id=patient_id, date=date, time=time
            )
            
            appointment_data = jsonable_encoder(appointment)

            return AppointmentResponse(**appointment_data)

        except HTTPException as e:
            raise e

        except Exception as e:
            raise NayaHttpResponse.internal_error()
    
    
    async def cancel_appointment(self, id: UUID,) -> AppointmentResponse:
        try:
            appointment =  TherapistService.cancel_appointment(
                self.session, id = id
            )
            return NayaHttpResponse.no_content()
        except Exception as e:
            raise NayaHttpResponse.internal_error() 

    async def list_appointments(self, token: str, patient_id: UUID | None = None) -> AppointmentResponse:
        try:

            decoded = decode_token(token)

            if decoded:
                user_id = decoded.get("sub")
            
            therapist = AuthService.get_therapist_by_user_id(self.session, user_id=user_id)

            appointments = await TherapistService.list_appointments( self.session, therapist_id=therapist.id, patient_id=patient_id)
            
            if not appointments:
                return NayaHttpResponse.not_found(
                    data={
                        "message": NayaResponseCodes.NO_APPOINTMENTS.detail,
                        "providedValue": str(therapist.id),
                    },
                    error_id=NayaResponseCodes.NO_APPOINTMENTS.code,
                )
            return appointments
            
        except Exception as e:
            raise e
          
    async def reschedule_appointment(self, token: str, id: UUID, date: date, time: time) -> AppointmentResponse:
        try:
            decoded = decode_token(token)
          
            if decoded:
                user_id = decoded.get("sub")
            
            therapist = AuthService.get_therapist_by_user_id(self.session, user_id=user_id)

            if TherapistService.appointment_exists(
            self.session, therapist_id=therapist.id, date= date, time=time
            ):
                NayaHttpResponse.bad_request(
                data={
                    "message": NayaResponseCodes.APPOINTMENT_EXISTS.detail,
                    "providedValue": {
                        "therapist_id": str(therapist.id),
                        "date": str(date),
                        "time": str(time)
                    },
                },
                error_id=NayaResponseCodes.APPOINTMENT_EXISTS.code,
            )
            appointment =  TherapistService.reschedule_appointment(
                self.session, id = id, date=date, time=time
            )
            return NayaHttpResponse.no_content()
        except Exception as e:
            raise e
        
    async def complete_appointment(self, id: UUID,) -> AppointmentResponse:
        try:
            appointment =  TherapistService.complete_appointment(
                self.session, id = id
            )
            return NayaHttpResponse.no_content()
        except Exception as e:
            raise NayaHttpResponse.internal_error() 
