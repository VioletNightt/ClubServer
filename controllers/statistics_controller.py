from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import MenuItem, OrderItem, ComputerRentalLog, Computer
from sqlalchemy import func
from datetime import datetime

router = APIRouter()

@router.get("/computer_usage")
async def get_computer_usage_stats(period: str, db: Session = Depends(get_db)):
    """Возвращает статистику использования компьютеров за день, месяц или год."""

    now = datetime.now()
    if period == "day":
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == "month":
        start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    elif period == "year":
        start_date = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    else:
        raise HTTPException(status_code=400, detail="Недопустимый период. Используйте 'day', 'month' или 'year'.")

    stats_query = (
        db.query(
            ComputerRentalLog.computer_id,
            func.count(ComputerRentalLog.id).label("rental_count"),
            func.sum(func.julianday(ComputerRentalLog.end_time) - func.julianday(ComputerRentalLog.start_time)).label(
                "total_rental_hours"),
            Computer.name.label("computer_name")
        )
        .join(Computer, ComputerRentalLog.computer_id == Computer.id)
        .filter(ComputerRentalLog.start_time >= start_date, ComputerRentalLog.end_time <= now)
        .group_by(ComputerRentalLog.computer_id, Computer.name)
    )

    stats = stats_query.all()

    results = [
        {
            "computer_name": stat.computer_name,
            "rental_count": stat.rental_count,
            "total_rental_hours": round(stat.total_rental_hours * 24, 2) if stat.total_rental_hours else 0
        }
        for stat in stats
    ]

    return results


@router.get("/food_statistics")
async def get_food_statistics(period: str, db: Session = Depends(get_db)):
    """Получает статистику заказов еды за указанный период"""
    today = datetime.today()

    if period == "day":
        start_date = today.replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == "month":
        start_date = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    elif period == "year":
        start_date = today.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    else:
        raise HTTPException(status_code=400, detail="Недопустимый период")

    statistics = (
        db.query(MenuItem.name, func.count(OrderItem.id).label("order_count"), func.sum(OrderItem.quantity * MenuItem.price).label("total_revenue"))
        .join(OrderItem, OrderItem.item_id == MenuItem.id)
        .filter(OrderItem.created_at >= start_date)
        .group_by(MenuItem.name)
        .all()
    )

    return [{"name": item.name, "order_count": item.order_count, "total_revenue": item.total_revenue} for item in statistics]
