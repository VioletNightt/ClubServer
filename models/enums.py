from enum import Enum

class ComputerStatus(Enum):
    AVAILABLE = "available"
    RENTED = "rented"
    OUT_OF_ORDER = "out_of_order"

class OrderStatus(Enum):
    PAID = "paid"
    PREPARING = "preparing"
    READY = "ready"
    DELIVERED = "delivered"

class UserRole(Enum):
    CLIENT = "client"
    STAFF = "staff"
