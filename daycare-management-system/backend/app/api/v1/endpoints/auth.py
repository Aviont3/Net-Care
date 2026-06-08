# Authentication Endpoints (Login, Register)
# ============================================

import logging
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.child import Parent
from app.schemas.auth import LoginRequest, Token, RefreshRequest, ParentActivateRequest, UserCreate, UserResponse
from app.core.security import verify_password, get_password_hash, create_access_token, create_refresh_token, decode_refresh_token
from app.core.config import settings
from app.dependencies import get_current_user, get_current_admin_user

router = APIRouter()

logger = logging.getLogger(__name__)


@router.post("/login", response_model=Token)
async def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """
    Staff login endpoint.
    Returns JWT access token for authentication.
    """
    # Find user by email
    user = db.query(User).filter(User.email == login_data.email).first()
    
    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user account"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires
    )
    
    # Create refresh token for token rotation
    refresh_token = create_refresh_token(data={"sub": user.email})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/refresh", response_model=Token)
async def refresh_token(request: RefreshRequest, db: Session = Depends(get_db)):
    """
    Token rotation endpoint.
    Exchange a valid refresh token for a new access + refresh token pair.
    Old refresh token is invalidated (single-use rotation).
    """
    payload = decode_refresh_token(request.refresh_token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    email = payload.get("sub")
    user = db.query(User).filter(User.email == email).first()
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )
    
    # Issue new token pair (rotation)
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    new_access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires
    )
    new_refresh_token = create_refresh_token(data={"sub": user.email})
    
    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }


@router.post("/setup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def initial_setup(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    One-time setup endpoint to create the first admin user.
    Only works when no users exist in the database.
    """
    existing_users = db.query(User).count()
    if existing_users > 0:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Setup already completed. Use /register with admin credentials."
        )

    # Force first user to be admin regardless of what's submitted
    new_user = User(
        email=user_data.email,
        password_hash=get_password_hash(user_data.password),
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        role="admin",
        is_active=True,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    logger.info("Initial admin user created: %s", new_user.email)

    return UserResponse(
        id=str(new_user.id),
        email=new_user.email,
        first_name=new_user.first_name,
        last_name=new_user.last_name,
        role=new_user.role,
        is_active=new_user.is_active
    )


@router.post("/parent/activate", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def activate_parent_account(
    request: ParentActivateRequest,
    db: Session = Depends(get_db),
):
    """
    Parent account activation.
    Parents use their invite code (generated during enrollment) to create
    a user account with role='parent' linked to their Parent record.
    """
    # Find parent by invite code
    parent = db.query(Parent).filter(Parent.invite_code == request.invite_code).first()
    if parent is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid invite code"
        )

    if parent.user_id is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account already activated"
        )

    if not parent.email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Parent record has no email address"
        )

    # Check if a user with this email already exists
    existing_user = db.query(User).filter(User.email == parent.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists"
        )

    # Create user account for parent
    new_user = User(
        email=parent.email,
        password_hash=get_password_hash(request.password),
        first_name=parent.first_name,
        last_name=parent.last_name,
        role="parent",
        is_active=True,
    )
    db.add(new_user)
    db.flush()

    # Link parent record to user account and clear invite code (single-use)
    parent.user_id = new_user.id
    parent.invite_code = None

    db.commit()
    db.refresh(new_user)

    logger.info("Parent account activated: %s", new_user.email)

    return UserResponse(
        id=str(new_user.id),
        email=new_user.email,
        first_name=new_user.first_name,
        last_name=new_user.last_name,
        role=new_user.role,
        is_active=new_user.is_active
    )


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Register a new user (admin only)."""
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    new_user = User(
        email=user_data.email,
        password_hash=get_password_hash(user_data.password),
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        role=user_data.role
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return UserResponse(
        id=str(new_user.id),
        email=new_user.email,
        first_name=new_user.first_name,
        last_name=new_user.last_name,
        role=new_user.role,
        is_active=new_user.is_active
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current authenticated user information"""
    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        role=current_user.role,
        is_active=current_user.is_active
    )