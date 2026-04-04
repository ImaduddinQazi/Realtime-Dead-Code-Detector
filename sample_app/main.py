from fastapi import FastAPI
from database import engine, Base
from routes import users, orders, legacy
from middleware import UsageTrackerMiddleware
import tracker

Base.metadata.create_all(bind=engine)  # tables created first
tracker.set_tables_ready()             # ← now tell tracker it's safe

app = FastAPI(title="Sample App (being monitored)")

app.add_middleware(UsageTrackerMiddleware)

app.include_router(users.router)
app.include_router(orders.router)
app.include_router(legacy.router)

@app.get("/")
def root():
    return {"status": "running"}