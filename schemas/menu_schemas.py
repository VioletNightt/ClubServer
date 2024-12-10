from pydantic import BaseModel

class MenuItemSchema(BaseModel):
    id: int
    name: str
    price: float

    class Config:
        from_attributes = True


class NewMenuItem(BaseModel):
    name: str
    price: float