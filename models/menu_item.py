from sqlalchemy import Column, Integer, String, Float,Boolean
from .base import Base
from sqlalchemy.orm import relationship

class MenuItem(Base):
    __tablename__ = "menu_items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    price = Column(Float)
    active = Column(Boolean, default=True)

    order_items = relationship("OrderItem", back_populates="menu_item")