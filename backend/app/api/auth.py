"""
Authentication API
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
    get_password_hash,
    verify_password,
)
from app.db.session import get_db
from app.models.models import User
from app.schemas.common import ApiResponse
from app.schemas.schemas import Token, UserCreate, UserResponse

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/register",
    response_model=ApiResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_user(
    user_in: UserCreate,
    db: Session = Depends(get_db),
):
    existing_user = (
        db.query(User)
        .filter(User.email == user_in.email)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already registered.",
        )

    user = User(
        email=user_in.email,
        hashed_password=get_password_hash(
            user_in.password
        ),
        full_name=user_in.full_name,
        role=user_in.role,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return ApiResponse(
        message="User registered successfully.",
        data=UserResponse.model_validate(user),
    )


@router.post(
    "/login",
    response_model=ApiResponse,
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = (
        db.query(User)
        .filter(User.email == form_data.username)
        .first()
    )

    if (
        user is None
        or not verify_password(
            form_data.password,
            user.hashed_password,
        )
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
        )

    access_token = create_access_token(
        {
            "sub": str(user.id),
            "role": user.role.value,
        }
    )

    token = Token(
        access_token=access_token,
        token_type="bearer",
        user=user,
    )

    return ApiResponse(
        message="Login successful.",
        data=token,
    )