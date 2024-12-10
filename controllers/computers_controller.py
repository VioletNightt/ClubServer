from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from pydantic import TypeAdapter
from models import Computer, ComputerStatus, User, UserRole, ComputerRentalLog
from schemas import ComputerSchema, ComputerCreateSchema, UpdateConfigurationSchema
from .auth_controller import get_current_user

router = APIRouter()

@router.get("/available", response_model=List[ComputerSchema])
async def get_available_computers(db: Session = Depends(get_db)):
    """Возвращает список доступных для аренды компьютеров."""
    available_computers = db.query(Computer).filter(Computer.active == True).filter(Computer.status == ComputerStatus.AVAILABLE).all()
    return available_computers

@router.get("/available_or_rented", response_model=List[ComputerSchema])
async def get_available_or_rented_computers(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Возвращает список доступных компьютеров или только арендованный текущим пользователем компьютер.
    """
    if current_user.role != UserRole.CLIENT:
        raise HTTPException(status_code=403, detail="Только клиенты могут просматривать доступные компьютеры")

    rented_computer = db.query(Computer).filter(Computer.active == True).filter(
        Computer.status == ComputerStatus.RENTED,
        Computer.rental_logs.any(user_id=current_user.id)
    ).first()

    if rented_computer:
        return TypeAdapter(List[ComputerSchema]).validate_python([rented_computer])

    available_computers = db.query(Computer).filter(Computer.active == True).filter(Computer.status == ComputerStatus.AVAILABLE).all()
    return TypeAdapter(List[ComputerSchema]).validate_python(available_computers)


@router.post("/rent")
async def rent_computer(
    computer_id: int,
    duration: str = Query(..., description="Длительность аренды (например, '10m' для 10 минут или '2h' для 2 часов)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Арендует выбранный компьютер на указанное время."""
    if current_user.role != UserRole.CLIENT:
        raise HTTPException(status_code=403, detail="Только клиенты могут арендовать компьютеры")

    computer = db.query(Computer).filter(Computer.id == computer_id).first()
    if not computer:
        raise HTTPException(status_code=404, detail="Компьютер не найден")
    if computer.status != ComputerStatus.AVAILABLE:
        raise HTTPException(status_code=400, detail="Компьютер уже арендован")

    try:
        if duration.endswith("m"):
            rental_duration = timedelta(minutes=int(duration[:-1]))
        elif duration.endswith("h"):
            rental_duration = timedelta(hours=int(duration[:-1]))
        else:
            raise ValueError("Неправильный формат длительности")
    except ValueError:
        raise HTTPException(status_code=400, detail="Неправильный формат длительности аренды")

    end_time = datetime.now() + rental_duration
    computer.status = ComputerStatus.RENTED
    computer.rental_end_time = end_time

    new_rental_log = ComputerRentalLog(
        computer_id=computer_id,
        user_id=current_user.id,  
        start_time=datetime.now(),
        end_time=end_time
    )
    db.add(new_rental_log)

    db.commit()
    return {
        "message": f"Компьютер {computer_id} успешно арендован",
        "rental_end_time": end_time.strftime("%Y-%m-%d %H:%M:%S")
    }


@router.get("", response_model=List[ComputerSchema])
async def get_computers(db: Session = Depends(get_db)):
    computers = db.query(Computer).filter(Computer.active == True).all()
    return computers

@router.post("", response_model=ComputerSchema)
async def add_computer(
    computer_data: ComputerCreateSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != UserRole.STAFF:
        raise HTTPException(status_code=403, detail="Только сотрудники могут добавлять компьютеры")

    new_computer = Computer(name=computer_data.name, configuration=computer_data.configuration)
    db.add(new_computer)
    db.commit()
    db.refresh(new_computer)
    return new_computer

@router.put("/{computer_id}", response_model=ComputerSchema)
async def update_computer(
    computer_id: int,
    data: UpdateConfigurationSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != UserRole.STAFF:
        raise HTTPException(status_code=403, detail="Только сотрудники могут изменять конфигурацию компьютеров")
    computer = db.query(Computer).filter(Computer.id == computer_id).first()
    if not computer:
        raise HTTPException(status_code=404, detail="Компьютер не найден")
    if computer.status == "rented":
        raise HTTPException(status_code=400, detail="Невозможно удалить арендованный компьютер")
    computer.configuration = data.configuration
    db.commit()
    db.refresh(computer)
    return computer

@router.delete("/{computer_id}", response_model=dict)
async def delete_computer(computer_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.STAFF:
        raise HTTPException(status_code=403, detail="Только сотрудники могут удалять компьютеры")
    computer = db.query(Computer).filter(Computer.id == computer_id).first()
    if not computer:
        raise HTTPException(status_code=404, detail="Компьютер не найден")
    if computer.status == "rented":
        raise HTTPException(status_code=400, detail="Невозможно удалить арендованный компьютер")
    computer.active = False
    db.commit()
    return {"message": "Компьютер успешно удален"}