from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from data_base.connect import get_db
from services.email import verify_token, create_verification_token
from services.users import confirm_email

router = APIRouter(prefix="/email", tags=["email"])

@router.get("/verify/{token}")
async def verify_email(token: str, db: Session = Depends(get_db)):
    try:
        email = verify_token(token)
        confirm_email(db, email)
        return {"message": "Email verified successfully"}
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token"
        )
