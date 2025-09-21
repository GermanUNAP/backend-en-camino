from database import db
from models.user import UserCreate, UserUpdate
from utils.auth import create_access_token
from passlib.context import CryptContext
import bcrypt

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def create_user(user: UserCreate):
    existing = db.find_one("users", {"username": user.username})
    if existing:
        raise ValueError("User already exists")
    hashed_password = pwd_context.hash(user.password)
    user_dict = user.dict()
    user_dict["password"] = hashed_password
    user_dict["is_active"] = True
    user_dict["is_staff"] = False
    user_dict["is_superuser"] = False
    result = db.insert_one("users", user_dict)
    return result

async def get_user(username: str):
    return db.find_one("users", {"username": username})

async def authenticate_user(username: str, password: str):
    user = await get_user(username)
    if not user or not pwd_context.verify(password, user["password"]):
        return False
    return user

async def create_access_token_for_user(user: dict):
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}