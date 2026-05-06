from sqlalchemy.orm import Session
from app.models.user import User
from app.utils.security import hash_password, verify_password, create_access_token
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserResponse


def authenticate_user(db: Session, username: str, password: str) -> User | None:
    """验证用户凭据，返回用户对象或None"""
    user = db.query(User).filter(User.username == username).first()
    if not user or not user.is_active:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def login(db: Session, request: LoginRequest) -> TokenResponse:
    user = authenticate_user(db, request.username, request.password)
    if not user:
        raise ValueError("用户名或密码错误")
    token = create_access_token({"sub": str(user.id), "role": user.role})
    return TokenResponse(access_token=token)


def admin_login(db: Session, request: LoginRequest) -> TokenResponse:
    user = authenticate_user(db, request.username, request.password)
    if not user:
        raise ValueError("用户名或密码错误")
    if not user.is_admin_role:
        raise ValueError("该账户无管理后台权限")
    token = create_access_token({"sub": str(user.id), "role": user.role})
    return TokenResponse(access_token=token)


def register(db: Session, request: RegisterRequest) -> UserResponse:
    """注册新用户"""
    existing = db.query(User).filter(
        (User.username == request.username) | (User.email == request.email)
    ).first()
    if existing:
        raise ValueError("用户名或邮箱已存在")
    user = User(
        username=request.username,
        email=request.email,
        hashed_password=hash_password(request.password),
        role=request.role,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return UserResponse(
        id=user.id, username=user.username, email=user.email,
        role=user.role, is_active=user.is_active,
    )


def get_current_user_info(user: User) -> UserResponse:
    """获取当前用户信息"""
    return UserResponse(
        id=user.id, username=user.username, email=user.email,
        role=user.role, is_active=user.is_active,
    )
