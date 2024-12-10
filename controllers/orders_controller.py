from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import get_db
from models.enums import UserRole, OrderStatus
from models.order import Order
from models.order_item import OrderItem
from schemas import CreateOrderSchema, OrderSchema, OrderDetailSchema
from models.user import User
from .auth_controller import get_current_user
from sqlalchemy.orm import joinedload

router = APIRouter()


@router.post("", response_model=dict)
async def create_order(
        order_data: CreateOrderSchema,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Создает новый заказ клиентом"""
    if current_user.role != UserRole.CLIENT:
        raise HTTPException(status_code=403, detail="Только клиенты могут оформлять заказы")

    new_order = Order(user_id=current_user.id, status="paid")
    db.add(new_order)
    db.commit()

    for item in order_data.items:
        order_item = OrderItem(order_id=new_order.id, item_id=item.item_id, quantity=item.quantity)
        db.add(order_item)

    db.commit()
    db.refresh(new_order)
    return {"message": "Заказ успешно создан"}

@router.get("", response_model=List[OrderSchema])
async def get_user_orders(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Возвращает список заказов текущего клиента."""
    if current_user.role != UserRole.CLIENT:
        raise HTTPException(status_code=403, detail="Только клиенты могут просматривать свои заказы")

    orders = db.query(Order).options(joinedload(Order.items).joinedload(OrderItem.menu_item)).filter(Order.user_id == current_user.id).all()

    result = [
        {
            "id": order.id,
            "user_id": order.user_id,
            "items": [{"item_id": item.item_id, "quantity": item.quantity, "name": item.menu_item.name, "price": item.menu_item.price} for item in order.items],
            "status": order.status,
            "total_price": order.total_price
        }
        for order in orders
    ]
    return result

@router.get("/pending", response_model=List[OrderDetailSchema])
async def get_pending_orders_for_staff(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    if current_user.role != UserRole.STAFF:
        raise HTTPException(status_code=403, detail="Только сотрудники могут просматривать заказы")

    orders = (
        db.query(Order)
        .options(
            joinedload(Order.items).joinedload(OrderItem.menu_item)
        )
        .filter(Order.status != OrderStatus.DELIVERED.value)
        .all()
    )

    results = []
    for order in orders:
        order_data = {
            "id": order.id,
            "user_id": order.user_id,
            "status": order.status,
            "total_price": order.total_price,
            "items": [
                {
                    "item_id": item.item_id,
                    "name": item.menu_item.name,
                    "price": item.menu_item.price,
                    "quantity": item.quantity
                }
                for item in order.items
            ]
        }
        results.append(order_data)

    return results


@router.put("/{order_id}/status")
async def update_order_status(
        order_id: int,
        new_status: OrderStatus = Query(...),
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Обновляет статус заказа."""
    if current_user.role != UserRole.STAFF:
        raise HTTPException(status_code=403, detail="Только сотрудники могут обновлять заказы")

    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Заказ не найден")

    current_status = OrderStatus(order.status) if isinstance(order.status, str) else order.status

    valid_transitions = {
        OrderStatus.PAID: [OrderStatus.PREPARING, OrderStatus.READY, OrderStatus.DELIVERED],
        OrderStatus.PREPARING: [OrderStatus.READY, OrderStatus.DELIVERED],
        OrderStatus.READY: [OrderStatus.DELIVERED]
    }

    if new_status not in valid_transitions.get(current_status, []):
        raise HTTPException(status_code=400, detail="Недопустимое изменение статуса заказа")

    order.status = new_status.value
    db.commit()
    db.refresh(order)
    return {"message": "Статус заказа успешно обновлен", "order_id": order_id, "new_status": new_status.value}
