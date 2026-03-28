from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import Order

router = APIRouter(prefix="/orders", tags=["orders"])

@router.get("/")
def get_orders(db: Session = Depends(get_db)):
    return db.query(Order).all()

@router.post("/{order_id}/confirm")
def confirm_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if order:
        order.status = "confirmed"
        db.commit()
    return order