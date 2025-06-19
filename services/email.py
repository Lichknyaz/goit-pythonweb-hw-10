from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from jose import jwt
from datetime import datetime, timedelta
from settings.email import get_settings
from settings.base import HASH_SECRET, HASH_ALGORITHM

email_settings = get_settings()

conf = ConnectionConfig(
    MAIL_USERNAME=email_settings.MAIL_USERNAME,
    MAIL_PASSWORD=email_settings.MAIL_PASSWORD,
    MAIL_FROM=email_settings.MAIL_FROM,
    MAIL_PORT=email_settings.MAIL_PORT,
    MAIL_SERVER=email_settings.MAIL_SERVER,
    MAIL_STARTTLS=email_settings.MAIL_STARTTLS,
    MAIL_SSL_TLS=email_settings.MAIL_SSL_TLS,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    MAIL_FROM_NAME=email_settings.MAIL_FROM_NAME,
)


async def send_verification_email(email: str, verification_token: str):
    verification_url = f"http://localhost:8000/email/verify/{verification_token}"

    message = MessageSchema(
        subject="Verify your email",
        recipients=[email],
        body=f"""
        Please verify your email by clicking on the link below:
        {verification_url}

        This link will expire in 24 hours.
        """,
        subtype="plain"
    )

    fm = FastMail(conf)
    await fm.send_message(message)


def create_verification_token(email: str) -> str:
    expire = datetime.today() + timedelta(
        minutes=email_settings.VERIFICATION_TOKEN_EXPIRE_MINUTES
    )
    return jwt.encode(
        {"exp": expire, "email": email},
        HASH_SECRET,
        algorithm=HASH_ALGORITHM
    )


def verify_token(token: str) -> str:
    try:
        payload = jwt.decode(token, HASH_SECRET, algorithms=[HASH_ALGORITHM])
        email: str = payload.get("email")
        if email is None:
            raise ValueError("Invalid token")
        return email
    except jwt.JWTError:
        raise ValueError("Invalid token")