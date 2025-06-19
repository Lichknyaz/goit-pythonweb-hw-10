from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from data_base.models import User
from schemas.user import UserModel
from services.auth import get_password_hash
from services.email import create_verification_token, send_verification_email

def confirm_email(db: Session, email: str) -> None:
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    user.confirmed = True
    db.commit()


async def create_user(body: UserModel, db: Session) -> User:
    existing_user = db.query(User).filter(User.email == body.email).first()
    if existing_user:
        raise HTTPException(status_code=409, detail="Email already registered")

    hashed_password = get_password_hash(body.password)
    new_user = User(
        name=body.name,
        email=body.email,
        phone=body.phone,
        birthday=body.birthday,
        hashed_password=hashed_password,
        confirmed=False
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    verification_token = create_verification_token(new_user.email)
    await send_verification_email(new_user.email, verification_token)

    return new_user