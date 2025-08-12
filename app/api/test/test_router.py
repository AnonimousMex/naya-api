
from typing import List
from fastapi import APIRouter, HTTPException, Header
from fastapi.encoders import jsonable_encoder

from app.api.test.test_controller import TestController
from app.api.test.test_schema import AnswersRequest, AnswersResponse, EmotionPercentageResponse, ListTestRequest , PostAnswerRequest, TestDetailsReponse, TestDetailsRequest, TestStoriesResponse, TestsResponse
from app.core.database import SessionDep
from app.core.http_response import NayaHttpResponse, NayaResponseModel

test_router = APIRouter(prefix="/test")

@test_router.get(
        "/init-test", 
        response_model=NayaResponseModel[TestStoriesResponse]
)
async def get_situtations(
    session: SessionDep, 
    token: str = Header(..., alias="Authorization")
):
    try:
        test_controller = TestController(session=session)
        data = await test_controller.get_stories(token=token)
        return NayaHttpResponse.ok(data=jsonable_encoder(data)) 
    except HTTPException as e:
        raise e
    except Exception as e:
        raise e
    
@test_router.post("/send-answer")
async def post_answer(session: SessionDep, request: PostAnswerRequest):
    try:
        test_controller = TestController(session=session)
        return await test_controller.post_answer(request)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise e
    
@test_router.post(
        "/list-answers",
        response_model=NayaResponseModel[List[AnswersResponse]]
)
async def list_answers(session: SessionDep, request: AnswersRequest ):
    try: 
        test_controller = TestController(session=session) 
        data = await test_controller.list_answers(request=request)
        return NayaHttpResponse.ok(data=jsonable_encoder(data))
    except HTTPException as e:
        raise e
    except Exception as e:
        raise e

@test_router.post(
        "/test-details",
        response_model=NayaResponseModel[TestDetailsReponse]
)
async def test_detail(session: SessionDep, request: TestDetailsRequest):
    try:
        test_controller = TestController(session=session)
        data = await test_controller.test_detail(request=request)
        return NayaHttpResponse.ok(data=jsonable_encoder(data))
    except HTTPException as e:
        raise e
    except Exception as e:
        raise e
    
@test_router.post(
        "/percentage-answers",
        response_model=NayaResponseModel[List[EmotionPercentageResponse]]
)
async def answers_details(session: SessionDep, request: AnswersRequest):
    try:
        test_conteoller = TestController(session=session)
        data = await test_conteoller.percentage_answers(request=request)
        return NayaHttpResponse.ok(data=jsonable_encoder(data))
    except HTTPException as e:
        raise e
    except Exception as e:
        raise e
    
@test_router.post(
        "/list-test",
        response_model=NayaResponseModel[List[TestsResponse]]
)
async def list_test(
    session: SessionDep, request: ListTestRequest):
    try:
        test_controller = TestController(session=session)
        tests = await test_controller.list_test(request)
        return NayaHttpResponse.ok(data=jsonable_encoder(tests))
    except HTTPException as e:
        raise e
    except Exception as e:
        raise e