from typing import Annotated
from pydantic import BaseModel
from fastapi import Request, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from authlib.integrations.starlette_client import OAuth
from app.core.settings import settings
from app.utils.security import decode_token
from app.api.users.user_service import UserService
from .database import SessionDep

oauth = OAuth()
oauth.register(
    name="google",
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)

oauth.register(
    name="github",
    client_id=settings.GITHUB_CLIENT_ID,
    client_secret=settings.GITHUB_CLIENT_SECRET,
    access_token_url="https://github.com/login/oauth/access_token",
    access_token_params=None,
    authorize_url="https://github.com/login/oauth/authorize",
    authorize_params=None,
    api_base_url="https://api.github.com/",
    client_kwargs={"scope": "user:email"},
)


class UserTokenSchema(BaseModel):
    id: str
    email: str
    name: str
    exp: int


class Oauth2AccessTokenBearer(OAuth2PasswordBearer):
    def __init__(self, auto_error=True):
        super().__init__(tokenUrl="/auth/login", auto_error=auto_error)

    async def __call__(self, request: Request, session: SessionDep) -> UserTokenSchema:
        token = await super().__call__(request=request)
        token_data = decode_token(token)
        if token_data is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Invalid or expired token"
            )
        self.verify_token_data_type(token_data=token_data)
        id, email, name, exp = self.get_user_token_data(token_data=token_data)
        user = await UserService.get_user_by_email(email=email, session=session)
        if not user or user is False:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Invalid or expired token"
            )
        return UserTokenSchema(id=id, email=email, name=name, exp=exp)

    def get_user_token_data(self, token_data: dict):
        try:
            id = token_data["sub"]
            email = token_data["user"]["email"]
            name = token_data["user"]["name"]
            exp = token_data["exp"]
            return id, email, name, exp
        except KeyError as e:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing field in token: {str(e)}",
            )

    def verify_token_data_type(self, token_data: dict) -> None:
        raise NotImplementedError("Use it in child classes")


class Oauth2AccessTokenBearerChild(Oauth2AccessTokenBearer):
    def verify_token_data_type(self, token_data: dict) -> None:
        if token_data and token_data.get("refresh"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Please provide an access token",
            )


class Oauth2RefreshTokenBearer(Oauth2AccessTokenBearer):
    def verify_token_data_type(self, token_data: dict) -> None:
        if token_data and not token_data.get("refresh"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Please provide a refresh token",
            )


oauth2_access_token = Oauth2AccessTokenBearerChild()
oauth2_refresh_token = Oauth2RefreshTokenBearer()

CurrentUser: UserTokenSchema = Depends(oauth2_access_token)
CurrentUserRefresh: UserTokenSchema = Depends(oauth2_refresh_token)
LoginFormDataDep = Annotated[OAuth2PasswordRequestForm, Depends()]
