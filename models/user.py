from sqlalchemy import Column, Integer, String, Enum
from sqlalchemy.orm import relationship
from passlib.context import CryptContext
from .base import Base
from .enums import UserRole

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    login = Column(String, unique=True, index=True, nullable=True)
    email = Column(String, unique=True, index=True, nullable=True)
    phone = Column(String, unique=True, index=True, nullable=True)
    role = Column(Enum(UserRole), default=UserRole.CLIENT)
    password_hash = Column(String, nullable=False)
    orders = relationship("Order", back_populates="user")
    rental_logs = relationship("ComputerRentalLog", back_populates="user")

    def set_password(self, password: str):
        """Установка хеша пароля"""
        self.password_hash = pwd_context.hash(password)

    def verify_password(self, password: str) -> bool:
        """Проверка пароля"""
        return pwd_context.verify(password, self.password_hash)
