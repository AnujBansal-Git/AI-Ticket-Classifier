from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.services.auth import hash_password

from app.auth.jwt_handler import create_access_token
from app.schemas.auth import RegisterRequest, TokenResponse
from app.services.auth import verify_password

from app.auth.dependencies import get_current_user
from app.schemas.auth import UserResponse
from fastapi.security import OAuth2PasswordRequestForm

from app.core.limiter import limiter

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)

@router.post("/register")
@limiter.limit("5/minute")
def register(
    request: Request,
    register_data: RegisterRequest,
    db: Session = Depends(get_db),
):
    existing_user = (
        db.query(User)
        .filter(User.username == register_data.username)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Username already exists.",
        )

    user = User(
        username=register_data.username,
        hashed_password=hash_password(register_data.password),
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "message": "User registered successfully.",
        "user_id": user.id,
    }

@router.post(
    "/login",
    response_model=TokenResponse,
)
@limiter.limit("5/minute")
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):

    user = (
        db.query(User)
        .filter(User.username == form_data.username)
        .first()
    )

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password.",
        )

    if not verify_password(
        form_data.password,
        user.hashed_password,
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password.",
        )

    access_token = create_access_token(
        {
            "sub": str(user.id),
        }
    )

    return TokenResponse(
        access_token=access_token,
    )

@router.get(
    "/me",
    response_model=UserResponse,
)
def get_me(
    current_user: User = Depends(get_current_user),
):
    return current_user