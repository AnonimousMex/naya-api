

from fastapi import APIRouter, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi import Header


from app.api.therapists.therapist_controller import TherapistController
from app.api.therapists.therapist_schema import TherapistCreateSchema, AppointmentRequest,  AppointmentResponse, EditAppointmentRequest, AppointmentListResponse, RescheduleAppointmentRequest
from app.core.database import SessionDep
from app.core.http_response import NayaHttpResponse, NayaResponseModel
from uuid import UUID


therapist_router = APIRouter()

@therapist_router.post(
    "/therapist",
    response_model=NayaResponseModel[TherapistCreateSchema]
)
async def create_therapist(therapist_data: TherapistCreateSchema, session: SessionDep):
    try:
        therapist_controller = TherapistController(session=session)

        therapist = await therapist_controller.create_therapist(
            therapist_data=therapist_data
        )

        return NayaHttpResponse.created(
            data=jsonable_encoder(therapist),
        )

    except HTTPException as e:
        raise e

    except Exception as e:
        raise e

@therapist_router.post(
    "/schedule-appointment",
    response_model=NayaResponseModel[AppointmentResponse]
)
async def schedule_appointment(request: AppointmentRequest, session: SessionDep, authorization: str = Header(...)):
    try:
        if not authorization:
            raise HTTPException(status_code=401, detail="Authorization header missing")

        token = authorization.replace("Bearer ", "")
        therapist_controller = TherapistController(session=session)

        appointment = await therapist_controller.create_appointment(
            token=token,
            patient_id=request.patient_id,
            date=request.date,
            time=request.time,
        )

        return NayaHttpResponse.created(
            data=jsonable_encoder(appointment),
        )

    except HTTPException as e:
        raise e

    except Exception as e:
        raise NayaHttpResponse.internal_error()

@therapist_router.put(
    "/cancel-appointment",
    response_model=NayaResponseModel[AppointmentResponse]
)
async def cancel_appointment(request: EditAppointmentRequest, session: SessionDep):
    try:
        therapist_controller = TherapistController(session=session)

        return await therapist_controller.cancel_appointment(appointment_id= request.appointment_id)

    except HTTPException as e:
        raise e

    except Exception as e:
        raise NayaHttpResponse.internal_error() 

@therapist_router.get(
    "/list-appointments",
    response_model=NayaResponseModel[list[AppointmentListResponse]]
)
async def list_appointments(
    session: SessionDep,
    authorization: str = Header(...),
    patient_id: UUID | None = None  
):
    try:
        if not authorization:
            raise HTTPException(status_code=401, detail="Authorization header missing")
        
        token = authorization.replace("Bearer ", "")

        therapist_controller = TherapistController(session=session)
        appointments = await therapist_controller.list_appointments(
            token=token,
            patient_id=patient_id  
        )

        return NayaHttpResponse.ok(data=jsonable_encoder(appointments))

    except HTTPException as e:
        raise e
    except Exception as e:
        raise e


@therapist_router.put(
    "/reschedule-appointment",
    response_model=NayaResponseModel[AppointmentResponse]
)
async def reschedule_appointment(request: RescheduleAppointmentRequest, session: SessionDep, authorization: str = Header(...)):
    try:
        if not authorization:
            raise HTTPException(status_code=401, detail="Authorization header missing")

        token = authorization.replace("Bearer ", "")
        therapist_controller = TherapistController(session=session)

        return await therapist_controller.reschedule_appointment(token=token, appointment_id= request.appointment_id, date= request.date, time= request.time)

    except HTTPException as e:
        raise e

    except Exception as e:
        raise NayaHttpResponse.internal_error() 
    

@therapist_router.put(
    "/complete-appointment",
    response_model=NayaResponseModel[AppointmentResponse]
)
async def reschedule_appointment(request: EditAppointmentRequest, session: SessionDep):
    try:
        therapist_controller = TherapistController(session=session)

        return await therapist_controller.complete_appointment(appointment_id= request.appointment_id)

    except HTTPException as e:
        raise e

    except Exception as e:
        raise NayaHttpResponse.internal_error() 
    


