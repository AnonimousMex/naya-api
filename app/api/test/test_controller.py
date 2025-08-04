from fastapi import HTTPException
from sqlmodel import Session

from app.api.auth.auth_service import AuthService
from app.api.test.test_schema import AnswersList, AnswersRequest, EmotionPercentageResponse, PostAnswerRequest, StoriesResponse, TestDetailsReponse, TestDetailsRequest, TestStoriesResponse
from app.api.test.test_service import TestService
from app.constants.response_codes import NayaResponseCodes
from app.core.http_response import NayaHttpResponse
from app.utils.security import decode_token


class TestController:
    def __init__(self, session: Session):
        self.session = session
    
    async def get_stories(self, token: str):
        try:
            decode = decode_token(token)
            if decode:
                user_id = decode.get("sub")
                
            test = await TestService.create_test(session=self.session, user_id=user_id)
            stories = await TestService.get_stories(session=self.session)
            response_stories = [
                StoriesResponse(
                    id=story["id"],
                    title=story["title"],
                    story=story["story"],
                    question_id=story["question_id"],
                    question=story["question"],
                    answers=[
                        AnswersList(
                            id=ans["id"], 
                            name=ans["name"],
                        )
                        for ans in story["answers"]
                    ]
                )
            for story in stories
            ]
            return TestStoriesResponse(test_id=test, stories=response_stories)
        except HTTPException as e:
            raise e
        except Exception as e:
            NayaHttpResponse.internal_error()

    async def post_answer(self, request: PostAnswerRequest ):
        try:
            test_complete = await TestService.is_test_complete(session=self.session, test_id=request.test_id)
            if test_complete == 5:
                NayaHttpResponse.bad_request(
                    data={
                        "message": NayaResponseCodes.TEST_COMPLETE.detail,
                    },
                    error_id=NayaResponseCodes.TEST_COMPLETE.code,
                )
            relation = await TestService.exist_relation_answer_test(
                session=self.session, 
                answer_id=request.answer_id, 
                test_id=request.test_id
            )
            if relation:
                NayaHttpResponse.bad_request(
                    data={
                        "message": NayaResponseCodes.DUPLICATE_RELATIONSHIP.detail,
                    },
                    error_id=NayaResponseCodes.DUPLICATE_RELATIONSHIP.code,
                )
            
            await TestService.relation_answer_test(
                session=self.session, 
                answer_id=request.answer_id, 
                test_id=request.test_id
            )
            return NayaHttpResponse.no_content()
        except HTTPException as e:
            raise e
        except Exception:
            NayaHttpResponse.internal_error()

    async def list_answers(self, request: AnswersRequest):
        try:
            return await TestService.list_answers(session=self.session, test_id=request.test_id)
        except Exception:
            NayaHttpResponse.internal_error()

    async def test_detail(self, request: TestDetailsRequest):
        try:
            user_id = await AuthService.get_user_id_by_patient_id(
                session=self.session, 
                patient_id=request.patient_id
            )
            count_answers = await TestService.is_test_complete(
                session=self.session, 
                test_id=request.test_id
            )
            data = await TestService.test_details(
                session= self.session, 
                test_id= request.test_id, 
                user_id= user_id
            )
            return TestDetailsReponse(date=data['date'], total_answers=count_answers, patient_name=data['name'],)
        except Exception:
            NayaHttpResponse.internal_error()

    async def percentage_answers(self, request: AnswersRequest):
        try:
            results = await TestService.get_percentage_results(session = self.session, test_id = request.test_id)
            if results:
                data = [
                    EmotionPercentageResponse(emotion_id=item[0], emotion_name=item[1], percentage=item[2])
                    for item in results  
                ]
                return data
            await TestService.create_answer_details(session= self.session, test_id= request.test_id)
            return await TestService.get_percentage_results(session = self.session, test_id = request.test_id)
        except Exception as e:
            raise e
