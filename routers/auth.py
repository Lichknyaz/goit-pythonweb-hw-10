from http.client import HTTPException

from fastapi import APIRouter, Depends, status, Query, HTTPException, Request
from sqlalchemy.orm import Session
from settings.base import ACCESS_TOKEN_EXPIRE_MINUTES
from data_base.connect import get_db
from data_base.models import User
from schemas.user import ResponseUserModel
from schemas.auth import TokenModel, EmailPasswordRequestForm
from services.auth import create_access_token, get_current_user, verify_password
from datetime import timedelta
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login", response_model=TokenModel)
async def login(form_data: EmailPasswordRequestForm
 = Depends(EmailPasswordRequestForm
), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=ResponseUserModel)
@limiter.limit("1/minute")
async def read_users_me(request: Request, current_user: User = Depends(get_current_user)):
    return current_user