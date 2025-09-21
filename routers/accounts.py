from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from models.user import User, UserCreate, UserUpdate
from crud.user import create_user, get_user, authenticate_user, create_access_token_for_user
from utils.auth import get_current_active_user
from typing import List

router = APIRouter()

@router.post("/users/", response_model=User)
async def create_new_user(user: UserCreate):
    user_db = await create_user(user)
    if not user_db:
        raise HTTPException(status_code=400, detail="User creation failed")
    return user_db

@router.get("/users/", response_model=List[User])
async def read_users(current_user: dict = Depends(get_current_active_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    users = db.find("users", {})
    return users

@router.get("/users/me", response_model=User)
async def read_users_me(current_user: dict = Depends(get_current_active_user)):
    return current_user

@router.put("/users/me", response_model=User)
async def update_users_me(
    current_user: dict = Depends(get_current_active_user),
    user_update: UserUpdate = None
):
    if user_update:
        await db.update_one("users", {"username": current_user["username"]}, user_update.dict(exclude_unset=True))
    updated_user = await get_user(current_user["username"])
    return updated_user

@router.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = await create_access_token_for_user(user)
    return access_token