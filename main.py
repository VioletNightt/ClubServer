from fastapi import FastAPI, Depends
from contextlib import asynccontextmanager
from controllers import auth_router, computers_router, menu_router, orders_router, statistics_router, user_router
from database import init_db
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime
import asyncio
from database import SessionLocal
from models import Computer
from models.enums import ComputerStatus

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    asyncio.create_task(rental_expiration_check())
    yield

app = FastAPI(
    docs_url="/docs",
    redoc_url=None,
    swagger_ui_oauth2_redirect_url="/auth/login",
    lifespan=lifespan
)

async def rental_expiration_check():
    """Фоновая задача для проверки завершения аренды компьютеров."""
    while True:
        now = datetime.now()
        with SessionLocal() as db:
            rented_computers = db.query(Computer).filter(Computer.status == ComputerStatus.RENTED).all()
            for computer in rented_computers:
                if computer.rental_end_time is not None and computer.rental_end_time <= now:
                    computer.status = ComputerStatus.AVAILABLE
                    computer.rental_end_time = None
                    db.commit()
        await asyncio.sleep(30)


app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(user_router, prefix="/users", tags=["users"], dependencies=[Depends(oauth2_scheme)])
app.include_router(computers_router, prefix="/computers", tags=["computers"], dependencies=[Depends(oauth2_scheme)])
app.include_router(menu_router, prefix="/menu", tags=["menu"], dependencies=[Depends(oauth2_scheme)])
app.include_router(orders_router, prefix="/orders", tags=["orders"], dependencies=[Depends(oauth2_scheme)])
app.include_router(statistics_router, prefix="/statistics", tags=["statistics"], dependencies=[Depends(oauth2_scheme)])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=5321)
