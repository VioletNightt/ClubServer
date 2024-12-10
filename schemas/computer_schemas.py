from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ComputerSchema(BaseModel):
    id: int
    name: str
    configuration: str
    status: str
    rental_end_time: Optional[datetime]

    class Config:
        from_attributes = True


class ComputerCreateSchema(BaseModel):
    name: str
    configuration: str


class UpdateConfigurationSchema(BaseModel):
    configuration: str