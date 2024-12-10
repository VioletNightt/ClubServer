from .auth_controller import router as auth_router
from .user_controller import router as user_router
from .computers_controller import router as computers_router
from .menu_controller import router as menu_router
from .orders_controller import router as orders_router
from .statistics_controller import router as statistics_router

__all__ = [
    "auth_router",
    "user_router",
    "computers_router",
    "menu_router",
    "orders_router",
    "statistics_router"
]

