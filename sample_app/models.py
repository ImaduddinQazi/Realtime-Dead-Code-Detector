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

class ApiUsageLog(Base):
    __tablename__ = "api_usage_logs"
    id = Column(Integer, primary_key=True)
    path = Column(String)
    method = Column(String)
    status_code = Column(Integer)
    timestamp = Column(DateTime, default=datetime.utcnow)

class DbTableUsage(Base):
    __tablename__ = "db_table_usage"
    id = Column(Integer, primary_key=True)
    table_name = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)