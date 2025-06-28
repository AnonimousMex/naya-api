from fastapi import HTTPException
from pydantic import BaseModel
from fastapi.responses import JSONResponse, Response
from typing import Generic, TypeVar, Optional


T = TypeVar("T")


class HttpResponseMessages:
    SUCCESS = "Success"
    CREATED = "Resource created"
    NO_CONTENT = "No content"
    UPDATED = "Resource updated"
    NOT_FOUND = "Resource not found"
    UNAUTHORIZED = (
        "User is not authorized to access this resource with an explicit deny"
    )
    FORBIDDEN = "Forbidden"
    INTERNAL_SERVER_ERROR = "Internal server error"
    BAD_REQUEST = "Bad request"


class HttpStatus:
    OK = 200
    CREATED = 201
    NO_CONTENT = 204
    NOT_FOUND = 404
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    INTERNAL_SERVER_ERROR = 500
    BAD_REQUEST = 400


class PaginationType(BaseModel):
    count: int
    currentPage: int
    nextPage: Optional[int] = None
    prevPage: Optional[int] = None
    lastPage: int


class NayaResponseModel(BaseModel, Generic[T]):
    status: int
    statusMessage: str
    data: Optional[T] = None
    pagination: Optional[PaginationType] = None


class NayaHttpResponse(Generic[T]):
    @staticmethod
    def ok(data: T, pagination: Optional[PaginationType] = None) -> JSONResponse:
        content = {
            "status": HttpStatus.OK,
            "statusMessage": HttpResponseMessages.SUCCESS,
            "data": data,
        }

        if isinstance(data, list):
            content["pagination"] = pagination.model_dump() if pagination else None

        return JSONResponse(
            status_code=HttpStatus.OK,
            content=content,
        )

    @staticmethod
    def created(data: T) -> JSONResponse:
        return JSONResponse(
            status_code=HttpStatus.CREATED,
            content={
                "status": HttpStatus.CREATED,
                "statusMessage": HttpResponseMessages.CREATED,
                "data": data,
            },
        )

    @staticmethod
    def no_content() -> Response:
        return Response(status_code=HttpStatus.NO_CONTENT)

    @staticmethod
    def updated(data: Optional[T] = None) -> JSONResponse:
        return JSONResponse(
            status_code=HttpStatus.OK,
            content={
                "status": HttpStatus.OK,
                "statusMessage": HttpResponseMessages.UPDATED,
                "data": data,
            },
        )

    @staticmethod
    def not_found(
        data: Optional[T] = None, error_id: Optional[str] = None
    ) -> HTTPException:
        raise HTTPException(
            status_code=HttpStatus.NOT_FOUND,
            detail={
                "status": HttpStatus.NOT_FOUND,
                "statusMessage": HttpResponseMessages.NOT_FOUND,
                "error": {
                    "code": error_id or HttpStatus.NOT_FOUND,
                    "data": data,
                },
            },
        )

    @staticmethod
    def unauthorized() -> HTTPException:
        raise HTTPException(
            status_code=HttpStatus.UNAUTHORIZED,
            detail={
                "status": HttpStatus.UNAUTHORIZED,
                "statusMessage": HttpResponseMessages.UNAUTHORIZED,
            },
        )

    @staticmethod
    def forbidden(
        data: Optional[T] = None, error_id: Optional[str] = None
    ) -> HTTPException:
        raise HTTPException(
            status_code=HttpStatus.FORBIDDEN,
            detail={
                "status": HttpStatus.FORBIDDEN,
                "statusMessage": HttpResponseMessages.FORBIDDEN,
                "error": {
                    "code": error_id or HttpStatus.FORBIDDEN,
                    "data": data,
                },
            },
        )

    @staticmethod
    def internal_error() -> HTTPException:
        raise HTTPException(
            status_code=HttpStatus.INTERNAL_SERVER_ERROR,
            detail={
                "status": HttpStatus.INTERNAL_SERVER_ERROR,
                "statusMessage": HttpResponseMessages.INTERNAL_SERVER_ERROR,
            },
        )

    @staticmethod
    def bad_request(data: T, error_id: Optional[str] = None) -> HTTPException:
        raise HTTPException(
            status_code=HttpStatus.BAD_REQUEST,
            detail={
                "status": HttpStatus.BAD_REQUEST,
                "statusMessage": HttpResponseMessages.BAD_REQUEST,
                "error": {
                    "code": error_id or HttpStatus.BAD_REQUEST,
                    "data": data,
                },
            },
        )
