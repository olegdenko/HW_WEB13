from fastapi import APIRouter, Depends, HTTPException, status, Security, Header
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import (
    OAuth2PasswordRequestForm,
    HTTPAuthorizationCredentials,
    HTTPBearer,
)
from sqlalchemy.orm import Session

# from src.database.models import User

from src.database.db import get_db
from src.repository import users as repository_users
from src.services.auth import auth_servise

# from src.database.models import User
from src.schemas import UserModel, UserResponse, TokenModel


# hash_handler = Hash()
security = HTTPBearer()
router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def signup(body: UserModel, db: Session = Depends(get_db)):
    exist_user = await repository_users.get_user_by_email(body.email, db)
    if exist_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Account already exists"
        )
    body.password = auth_servise.get_password_hash(body.password)
    new_user = await repository_users.create_user(body, db)

    return new_user


@router.post("/login", response_model=TokenModel)
async def login(
    body: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user = await repository_users.get_user_by_email(body.username, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="401 UNAUTHORIZED Invalid email",
        )
    if not auth_servise.verify_password(body.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="401 UNAUTHORIZED Invalid password",
        )
    # Generate JWT
    access_token = await auth_servise.create_access_token(data={"sub": user.email})
    refresh_token = await auth_servise.create_refresh_token(data={"sub": user.email})
    await repository_users.update_token(user, refresh_token, db)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


# @router.post("/login", response_model=TokenModel)
# async def login(
#     body: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
# ):
#     user = await repository_users.get_user_by_email(body.username, db)
#     if user is None:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="401 UNAUTHORIZED Invalid email",
#         )
#     if not auth_servise.verify_password(body.password, user.password):
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="401 UNAUTHORIZED Invalid password",
#         )

#     # Generate JWT
#     access_token = await auth_servise.create_access_token(data={"sub": user.email})
#     refresh_token = await auth_servise.create_refresh_token(data={"sub": user.email})
#     await repository_users.update_token(user, refresh_token, db)

#     # Перенаправляємо користувача на головну сторінку
#     redirect_url = "/"
#     response = RedirectResponse(url=redirect_url)

#     # Додаємо токени до cookies
#     response.set_cookie("access_token", access_token)
#     response.set_cookie("refresh_token", refresh_token)

#     return response


@router.get("/refresh_token", response_model=TokenModel)
async def refresh_token(
    credentials: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(get_db),
):
    token = credentials.credentials
    email = await auth_servise.decode_refresh_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user.refresh_token != token:
        await repository_users.update_token(user, None, db)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )

    access_token = await auth_servise.create_access_token(data={"sub": email})
    refresh_token = await auth_servise.create_refresh_token(data={"sub": email})
    await repository_users.update_token(user, refresh_token, db)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


# @router.get("/")
# async def root():
#     return {"message": "Hello World"}


# @router.get("/secret")
# async def read_item(current_user: User = Depends(get_current_user)):
#     return {"message": "secret router", "owner": current_user.email}
