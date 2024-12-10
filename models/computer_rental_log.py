from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from .base import Base

class ComputerRentalLog(Base):
    __tablename__ = "computer_rental_logs"

    id = Column(Integer, primary_key=True, index=True)
    computer_id = Column(Integer, ForeignKey("computers.id"), index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=True)

    computer = relationship("Computer", back_populates="rental_logs")
    user = relationship("User", back_populates="rental_logs")
