from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas import LoginRequest
from ..models import User
from ..config import settings
from ..utils.security import create_jwt
from passlib.hash import bcrypt

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not bcrypt.verify(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_jwt(settings.JWT_SECRET, str(user.id), settings.JWT_EXPIRE_MINUTES)
    return {"access_token": token, "token_type": "bearer", "user": {"id": user.id, "name": user.name, "email": user.email}}
