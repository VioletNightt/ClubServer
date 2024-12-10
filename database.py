from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, User, UserRole, Computer, MenuItem
from passlib.context import CryptContext


DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def init_db():
    Base.metadata.create_all(bind=engine)

    with SessionLocal() as session:
        if not session.query(User).first():
            admin_user = User(
                login="admin",
                email="admin@example.com",
                phone="123456789",
                role=UserRole.STAFF,
                password_hash=pwd_context.hash("admin")
            )
            session.add(admin_user)

        if not session.query(Computer).first():
            computers = [
                Computer(name="PC1", configuration="GIGABYTE Core i7-10700F, 32ГБ DDR4, 1ТБ SSD + 512гб ssd, RTX3060 12GB, Win 10 PRO, 700 Вт"),
                Computer(name="PC2", configuration="RTX 4060ti i5 12400f 16gb 1tb ssd m2"),
                Computer(name="PC3", configuration="ASUS TUF Core i7 14700 16ядер, 32ГБ DDR5, RTX4080 16GB, 1+1Тb SSD, 850W")
            ]
            session.add_all(computers)

        if not session.query(MenuItem).first():
            menu_items = [
                MenuItem(name="Капучино", price=400),
                MenuItem(name="Чай", price=200),
                MenuItem(name="Сэндвич", price=300)
            ]
            session.add_all(menu_items)

        session.commit()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
