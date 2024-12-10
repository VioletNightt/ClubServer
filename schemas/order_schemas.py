from pydantic import BaseModel
from typing import List

class CreateOrderItemSchema(BaseModel):
    item_id: int
    quantity: int

class OrderItemSchema(BaseModel):
    item_id: int
    quantity: int

    class Config:
        from_attributes = True

class OrderSchema(BaseModel):
    id: int
    user_id: int
    items: List[OrderItemSchema]
    status: str
    total_price: float

    class Config:
        from_attributes = True

class CreateOrderSchema(BaseModel):
    items: List[CreateOrderItemSchema]

class OrderItemDetailSchema(BaseModel):
    item_id: int
    name: str
    price: float
    quantity: int

    class Config:
        from_attributes = True

class OrderDetailSchema(BaseModel):
    id: int
    user_id: int
    items: List[OrderItemDetailSchema]
    status: str
    total_price: float

    class Config:
        from_attributes = True
