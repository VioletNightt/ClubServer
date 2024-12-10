from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import MenuItem, UserRole
from schemas import MenuItemSchema, NewMenuItem
from models import User
from .auth_controller import get_current_user

router = APIRouter()

@router.get("", response_model=List[MenuItemSchema])
async def get_menu(db: Session = Depends(get_db)):
    return db.query(MenuItem).filter(MenuItem.active == True).all()

@router.post("", response_model=MenuItemSchema)
async def add_menu_item(
    item_data: NewMenuItem,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    print(current_user.login, current_user.role)
    if current_user.role != UserRole.STAFF:
        raise HTTPException(status_code=403, detail="Только сотрудники могут добавлять блюда в меню.")

    new_item = MenuItem(name=item_data.name, price=item_data.price)
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item

@router.put("/{item_id}/price")
async def update_menu_item_price(item_id: int, new_price: float, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Обновление элемента меню (только для сотрудников)"""
    if current_user.role != UserRole.STAFF:
        raise HTTPException(status_code=403, detail="Только сотрудники могут изменять цену.")
    item = db.query(MenuItem).get(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Блюдо не найдено.")
    item.price = new_price
    db.commit()
    return {"message": "Цена блюда успешно обновлена."}

@router.delete("/{item_id}")
async def delete_menu_item(item_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Удаление элемента меню (только для сотрудников)"""
    if current_user.role != UserRole.STAFF:
        raise HTTPException(status_code=403, detail="Только сотрудники могут удалять блюда.")
    item = db.query(MenuItem).get(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Блюдо не найдено.")
    item.active = False
    db.commit()
    return {"message": "Блюдо успешно удалено из меню."}
