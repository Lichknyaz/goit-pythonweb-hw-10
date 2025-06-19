from fastapi import Depends, HTTPException, status, APIRouter, UploadFile, File
from sqlalchemy.orm import Session
from data_base.connect import get_db
from data_base.models import User
from datetime import date, timedelta
from typing import List
from sqlalchemy import and_
from sqlalchemy.exc import IntegrityError
from services.auth import get_current_user, get_password_hash
from schemas.user import UserModel, UserUpdateModel, ResponseUserModel
from services.avatar import upload_avatar


router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=ResponseUserModel)
def create_user(user: UserModel, db: Session = Depends(get_db)):
    # Check if email exists
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    hashed_password = get_password_hash(user.password)
    db_user = User(
        name=user.name,
        email=user.email,
        phone=user.phone,
        birthday=user.birthday,
        hashed_password=hashed_password
    )

    db.add(db_user)
    try:
        db.commit()
        db.refresh(db_user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User creation failed"
        )
    return db_user


@router.post("/avatar")
def upload_user_avatar(file: UploadFile = File(...),
                       db: Session = Depends(get_db),
                       current_user: User = Depends(get_current_user)):
    url = upload_avatar(file.file)
    current_user.avatar = url
    db.commit()
    return {"avatar": url}


@router.get("/", response_model=List[ResponseUserModel])
def get_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    name: str | None = None,
    email: str | None = None,
    phone: str | None = None
):
    users = db.query(User)
    if name:
        users = users.filter(User.name.ilike(f"%{name}%"))
    if email:
        users = users.filter(User.email.ilike(f"%{email}%"))
    if phone:
        users = users.filter(User.phone.ilike(f"%{phone}%"))
    return users.all()


@router.get("/birthdays", response_model=List[ResponseUserModel])
def get_birthdays(db: Session = Depends(get_db),
                  current_user: User = Depends(get_current_user),
                  days_ahead: int = 0):
    today = date.today()
    upcoming_date = today + timedelta(days=days_ahead)
    users = db.query(User).all()
    upcoming_birthdays = []

    for user in users:
        if user.birthday:
            birthday_this_year = user.birthday.replace(year=today.year)
            if today <= birthday_this_year <= upcoming_date:
                upcoming_birthdays.append(user)
    return upcoming_birthdays


@router.get("/{user_id}", response_model=ResponseUserModel)
def get_user(user_id: int,
             db: Session = Depends(get_db),
             current_user: User = Depends(get_current_user)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@router.patch("/{user_id}", response_model=ResponseUserModel)
def update_user(
    user_id: int,
    user_update: UserUpdateModel,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    db_user = db.query(User).filter(User.id == user_id).first()

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    if user_update.email and user_update.email != db_user.email:
        email_check = db.query(User).filter(and_(User.email == user_update.email,
                                                 User.id != user_id)).first()
        if email_check:
            raise HTTPException(status_code=400, detail="Email already in use")

    update_data = user_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_user, field, value)

    db.commit()
    db.refresh(db_user)
    return db_user


@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(db_user)
    db.commit()
    return f'User id: {user_id} has been deleted'