from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import User

router=APIRouter(prefix="/users",tags=["users"])

@router.get("/")
def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()

@router.post("/")
def create_user(name: str, email:str, db: Session = Depends(get_db)):
    user=User(name=name, email=email)
    db.add(user)
    db.commit()
    return user
