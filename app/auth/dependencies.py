from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session

from app.auth.jwt_handler import verify_access_token
from app.db.session import get_db
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="auth/login"
)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):

    try:
        payload = verify_access_token(token)

        user_id = int(payload["sub"])

    except (JWTError, KeyError, ValueError):

        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token.",
        )

    user = db.get(User, user_id)

    if user is None:

        raise HTTPException(
            status_code=401,
            detail="User not found.",
        )

    return user