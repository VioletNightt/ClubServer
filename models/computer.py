from sqlalchemy import Column, Integer, String, Enum, DateTime, Boolean
from .base import Base
from .enums import ComputerStatus
from sqlalchemy.orm import relationship

class Computer(Base):
    __tablename__ = "computers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    configuration = Column(String, index=True)
    status = Column(Enum(ComputerStatus), default=ComputerStatus.AVAILABLE)
    rental_end_time = Column(DateTime, nullable=True)
    active = Column(Boolean, default=True)

    rental_logs = relationship("ComputerRentalLog", back_populates="computer")