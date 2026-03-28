from fastapi import FastAPI
from database import engine, Base
from routes import users, orders, legacy

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Sample App (being monitored)")

app.include_router(users.router)
app.include_router(orders.router)
app.include_router(legacy.router)

@app.get("/")
def root():
    return {"status": "running"}