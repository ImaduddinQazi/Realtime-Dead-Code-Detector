from fastapi import FastAPI
from detector_core.database import engine, Base
from sample_app_fastapi.routes import users, orders, legacy
from sample_app_fastapi.routes import dashboard          # ← add this
from sample_app_fastapi.middleware import UsageTrackerMiddleware
from detector_core import tracker

Base.metadata.create_all(bind=engine)
tracker.set_tables_ready()

app = FastAPI(title="Sample App (being monitored)")

app.add_middleware(UsageTrackerMiddleware)

app.include_router(users.router)
app.include_router(orders.router)
app.include_router(legacy.router)
app.include_router(dashboard.router)  # ← add this

@app.get("/")
def root():
    return {"status": "running"}