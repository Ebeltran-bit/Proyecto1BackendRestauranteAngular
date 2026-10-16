from fastapi import APIRouter, Depends, HTTPException, status

from app.data.user_store import user_store
from app.routers.dependencies import get_current_user, get_token
from app.schemas import LoginRequest, LoginResponse, User

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/login",
    response_model=LoginResponse,
    summary="Log in and receive the token for the other requests",
    responses={status.HTTP_401_UNAUTHORIZED: {"description": "Wrong username or password"}},
)
def login(body: LoginRequest) -> LoginResponse:
    user = user_store.authenticate(body.username.lower(), body.password)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario o contraseña incorrectos")
    return LoginResponse(access_token=user_store.open_session(user.id), user=user)


@router.get("/me", response_model=User, summary="Who is logged in with this token")
def me(user: User = Depends(get_current_user)) -> User:
    return user


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT, summary="Close the session of this token")
def logout(token: str = Depends(get_token)) -> None:
    user_store.close_session(token)
