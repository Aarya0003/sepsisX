from typing import Generator, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import get_current_user, get_current_active_user, get_current_superuser
from app.db.database import get_db
from app.db.models import User, RoleType

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/token")

def get_current_doctor_or_admin(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """
    Dependency to ensure user is a doctor or admin
    """
    if current_user.role != RoleType.DOCTOR and current_user.role != RoleType.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges",
        )
    return current_user

def get_current_nurse_or_above(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """
    Dependency to ensure user is a nurse, doctor, or admin
    """
    if (current_user.role != RoleType.NURSE and 
        current_user.role != RoleType.DOCTOR and 
        current_user.role != RoleType.ADMIN):
        
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges",
        )
    return current_user