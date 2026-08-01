from __future__ import annotations

from functools import lru_cache

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from app.core.startup import app_state
from app.db.session import get_db
from app.models.models import User
from app.core.security import SECRET_KEY, ALGORITHM

from app.agents.supervisor.supervisor import Supervisor


# ---------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login"
)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Return the authenticated user.
    """

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )

        user_id = payload.get("sub")

        if user_id is None:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    user = (
        db.query(User)
        .filter(User.id == int(user_id))
        .first()
    )

    if user is None:
        raise credentials_exception

    return user


# ---------------------------------------------------------------------
# Supervisor Dependency
# ---------------------------------------------------------------------

@lru_cache(maxsize=1)
def get_supervisor() -> Supervisor:
    """
    Returns a singleton Supervisor instance.

    The Supervisor owns the complete
    multi-agent workflow.
    """

    return Supervisor()

def get_supervisor():
    if app_state.supervisor is None:
        raise RuntimeError("Supervisor has not been initialized.")
    return app_state.supervisor