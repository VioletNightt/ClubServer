from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import User, UserRole
from schemas import StaffSchema, RegisterUser, ChangePasswordSchema
from .auth_controller import get_current_user

router = APIRouter()

@router.get("/staffs", response_model=List[StaffSchema])
async def get_staffs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Возвращает список сотрудников."""
    if current_user.role != UserRole.STAFF:
        raise HTTPException(status_code=403, detail="Только сотрудники могут просматривать список сотрудников.")
    staffs = db.query(User).filter(User.role == UserRole.STAFF).all()
    return staffs


@router.post("/register")
def register(user: RegisterUser, db: Session = Depends(get_db)):
    """Регистрация сотрудника"""
    if db.query(User).filter((User.email == user.email) | (User.login == user.login)).first():
        raise HTTPException(status_code=400, detail="Логин или email уже зарегистрированы")

    new_user = User(
        login=user.login,
        email=str(user.email),
        phone=user.phone,
        role=UserRole.STAFF
    )
    new_user.set_password(user.password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "Пользователь успешно зарегистрирован"}

@router.delete("/{staff_id}")
async def delete_staff(
    staff_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Удаляет сотрудника."""
    if current_user.role != UserRole.STAFF:
        raise HTTPException(status_code=403, detail="Доступ запрещен")
    if current_user.id == staff_id:
        raise HTTPException(status_code=400, detail="Нельзя удалить самого себя")

    staff_to_delete = db.query(User).filter(User.id == staff_id, User.role == UserRole.STAFF).first()
    if not staff_to_delete:
        raise HTTPException(status_code=404, detail="Сотрудник не найден")

    db.delete(staff_to_delete)
    db.commit()
    return {"message": "Сотрудник успешно удален"}

@router.put("/{staff_id}/password")
async def change_password(
    staff_id: int,
    data: ChangePasswordSchema,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Меняет пароль для текущего пользователя."""
    if current_user.role != UserRole.STAFF:
        raise HTTPException(status_code=403, detail="Доступ запрещен")
    if current_user.id != staff_id:
        raise HTTPException(status_code=403, detail="Вы можете изменить пароль только для своей учетной записи")

    user = db.query(User).filter(User.id == staff_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    user.set_password(data.password)
    db.commit()
    return {"message": "Пароль успешно изменен"}

