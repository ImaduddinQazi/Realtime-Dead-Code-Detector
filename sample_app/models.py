from database import Base
from sqlalchemy import Column, Integer, String, DateTime, Float
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    total = Column(Float)
    status = Column(String, default="pending")

class LegacyPayment(Base):
    __tablename__ = "legacy_payments"   # ← this table will show as dead
    id = Column(Integer, primary_key=True)
    old_ref = Column(String)
    amount = Column(Float)