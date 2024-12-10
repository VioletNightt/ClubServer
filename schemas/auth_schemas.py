from pydantic import BaseModel, EmailStr

class RegisterUser(BaseModel):
    login: str
    email: EmailStr
    phone: str
    password: str

class LoginUser(BaseModel):
    login_or_email: str
    password: str
