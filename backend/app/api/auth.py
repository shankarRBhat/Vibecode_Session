from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.security import create_access_token, create_refresh_token, decode_token, hash_password, verify_password
from app.database.session import get_db
from app.models.entities import User, UserRole, UserRoleAssignment
from app.schemas.auth import LoginRequest, RefreshRequest, RegisterRequest, TokenResponse, UserResponse

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])
bearer = HTTPBearer(auto_error=False)


def _get_roles(db: Session, user_id) -> list[str]:
    return list(db.scalars(select(UserRoleAssignment.role).where(UserRoleAssignment.user_id == user_id)).all())


def _user_response(db: Session, user: User) -> UserResponse:
    return UserResponse.model_validate({**user.__dict__, "roles": _get_roles(db, user.id)})


def _tokens(db: Session, user: User) -> TokenResponse:
    roles = _get_roles(db, user.id)
    return TokenResponse(
        access_token=create_access_token(str(user.id), roles),
        refresh_token=create_refresh_token(str(user.id), roles),
        user=_user_response(db, user),
    )


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> TokenResponse:
    if payload.role == UserRole.ADMIN:
        raise HTTPException(status_code=403, detail={"code": "ADMIN_REGISTRATION_DISABLED", "message": "Admin accounts are provisioned by the system"})
    if db.scalar(select(User).where(User.email == payload.email.lower())):
        raise HTTPException(status_code=409, detail={"code": "EMAIL_ALREADY_REGISTERED", "message": "Email is already registered"})
    user = User(email=payload.email.lower(), password_hash=hash_password(payload.password), full_name=payload.full_name, phone=payload.phone)
    db.add(user)
    db.flush()
    db.add(UserRoleAssignment(user_id=user.id, role=payload.role.value))
    db.commit()
    db.refresh(user)
    return _tokens(db, user)


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    user = db.scalar(select(User).where(User.email == payload.email.lower()))
    if user is None or not user.is_active or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail={"code": "INVALID_CREDENTIALS", "message": "Email or password is incorrect"})
    return _tokens(db, user)


@router.post("/refresh", response_model=TokenResponse)
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)) -> TokenResponse:
    claims = decode_token(payload.refresh_token, expected_type="refresh")
    user = db.get(User, claims["sub"])
    if user is None or not user.is_active:
        raise HTTPException(status_code=401, detail={"code": "USER_INACTIVE", "message": "User is not active"})
    return _tokens(db, user)


def get_current_user(credentials: HTTPAuthorizationCredentials | None = Depends(bearer), db: Session = Depends(get_db)) -> User:
    if credentials is None:
        raise HTTPException(status_code=401, detail={"code": "AUTHENTICATION_REQUIRED", "message": "Bearer token required"}, headers={"WWW-Authenticate": "Bearer"})
    claims = decode_token(credentials.credentials)
    user = db.get(User, claims["sub"])
    if user is None or not user.is_active:
        raise HTTPException(status_code=401, detail={"code": "USER_INACTIVE", "message": "User is not active"})
    return user


def require_roles(*allowed_roles: UserRole):
    allowed = {role.value for role in allowed_roles}

    def dependency(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> User:
        if not allowed.intersection(_get_roles(db, user.id)):
            raise HTTPException(status_code=403, detail={"code": "FORBIDDEN", "message": "You do not have permission for this resource"})
        return user

    return dependency


@router.get("/me", response_model=UserResponse)
def me(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> UserResponse:
    return _user_response(db, user)
