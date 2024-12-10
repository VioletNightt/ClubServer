from pydantic import BaseModel

class StaffSchema(BaseModel):
    id: int
    login: str
    email: str
    phone: str

    class Config:
        from_attributes = True


class ChangePasswordSchema(BaseModel):
    password: str