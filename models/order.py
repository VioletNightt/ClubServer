from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.orm import relationship
from .base import Base
from sqlalchemy.ext.hybrid import hybrid_property

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id")) 
    status = Column(String)

    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")


    @hybrid_property
    def total_price(self):
        return sum(item.menu_item.price * item.quantity for item in self.items)