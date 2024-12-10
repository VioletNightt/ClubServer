from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from .base import Base
from datetime import datetime

class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    item_id = Column(Integer, ForeignKey("menu_items.id"))
    quantity = Column(Integer)
    created_at = Column(DateTime, default=datetime.now())

    order = relationship("Order", back_populates="items")
    menu_item = relationship("MenuItem", back_populates="order_items")
