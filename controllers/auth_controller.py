from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import JWTError, jwt
from database import get_db
from models import User, UserRole
from schemas import RegisterUser, LoginUser
from passlib.context import CryptContext


SECRET_KEY = "1fe7fc06-6332-44d2-abb2-b0f68bc3a3c1"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


from fastapi.security import OAuth2PasswordBearer
from fastapi import HTTPException, status, Request

class CustomOAuth2PasswordBearer(OAuth2PasswordBearer):
    async def __call__(self, request: Request) -> str:
        authorization: str = request.headers.get("Authorization")
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Вы не авторизованы. Пожалуйста, выполните вход.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return await super().__call__(request)

oauth2_scheme = CustomOAuth2PasswordBearer(tokenUrl="auth/login")


async def get_current_user(
        token: str = Depends(oauth2_scheme),
        app_source: str = Header(..., alias="X-App-Source"),
        db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не удалось подтвердить учетные данные",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_login: str = payload.get("sub")
        if user_login is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.login == user_login).first()
    if user is None:
        raise credentials_exception

    if (user.role == UserRole.STAFF and app_source != "staff") or \
            (user.role == UserRole.CLIENT and app_source != "client"):
        raise HTTPException(status_code=403, detail="Доступ запрещен для данного пользователя")

    return user

@router.post("/register_client")
def register_client(user: RegisterUser, db: Session = Depends(get_db)):
    if db.query(User).filter(
            (User.email == user.email) | (User.login == user.login) | (User.phone == user.phone)).first():
        raise HTTPException(status_code=400, detail="Логин, email или номер телефона уже зарегистрированы")

    new_client = User(
        login=user.login,
        email=str(user.email),
        phone=user.phone,
        role=UserRole.CLIENT
    )
    new_client.set_password(user.password)
    db.add(new_client)
    db.commit()
    db.refresh(new_client)
    return {"message": "Клиент успешно зарегистрирован"}


@router.post("/login")
def login(user: LoginUser, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(
        (User.login == user.login_or_email) | (User.email == user.login_or_email)
    ).first()

    if db_user is None or not db_user.verify_password(user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный логин/email или пароль"
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": db_user.login}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer", "role": db_user.role}