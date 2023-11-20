from sqlalchemy.orm import Session
from libgravatar import Gravatar
from src.database.models import User
from src.schemas import UserModel


async def get_user_by_email(email, db: Session) -> User | None:
    return db.query(User).filter_by(email=email).first()


async def create_user(body: UserModel, db: Session):
    g = Gravatar(body.email)
    new_user = User(**body.model_dump(), avatar=g.get_image())
    # new_user = User(**body.model_dump(), avatar=g.get_image(), roles=["user"])
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


# TODO додавання аватару

# async def create_user(body: UserModel, db: Session):
#     g = Gravatar(body.email)
#     avatar_url = g.get_image()
#     if body.avatar:
#         contents = await body.avatar.read()
#         avatar_url = save_uploaded_file(contents, body.avatar.filename)

#     new_user = User(**body.model_dump(), avatar=avatar_url)
#     db.add(new_user)
#     db.commit()
#     db.refresh(new_user)
#     return new_user


async def update_token(user: User, refresh_token, db: Session):
    user.refresh_token = refresh_token
    db.commit()


async def confirmed_email(email: str, db: Session) -> None:
    user = await get_user_by_email(email, db)
    user.confirmed = True
    db.commit()
