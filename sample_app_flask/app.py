from flask import Flask, request, g
import time
from detector_core.database import engine, Base, SessionLocal
from detector_core.models import ApiUsageLog
from detector_core import tracker

Base.metadata.create_all(bind=engine)
tracker.set_tables_ready()

app = Flask(__name__)

IGNORED_PATHS = {"/favicon.ico"}

@app.before_request
def start_timer():
    g.start_time = time.time()

@app.after_request
def log_request(response):
    if request.path not in IGNORED_PATHS:
        db = SessionLocal()
        try:
            log = ApiUsageLog(
                path=request.path,
                method=request.method,
                status_code=response.status_code,
            )
            db.add(log)
            db.commit()
        except Exception as e:
            db.rollback()
            print(f"Middleware error: {e}")
        finally:
            db.close()
    return response

# Sample routes — same pattern as FastAPI version
@app.route("/users", methods=["GET"])
def get_users():
    return {"message": "list of users"}

@app.route("/users", methods=["POST"])
def create_user():
    return {"message": "user created"}

@app.route("/orders", methods=["GET"])
def get_orders():
    return {"message": "list of orders"}

@app.route("/orders/<int:order_id>/confirm", methods=["POST"])
def confirm_order(order_id):
    return {"message": f"order {order_id} confirmed"}

# Legacy routes — intentionally never called
@app.route("/v1/old-payment", methods=["GET"])
def old_payment():
    return {"message": "legacy endpoint"}

@app.route("/v1/legacy-signup", methods=["POST"])
def legacy_signup():
    return {"message": "legacy endpoint"}

# Dashboard & API report — reuses the same analyzer engine
from detector_core.analyzer import analyze_routes, analyze_tables

@app.route("/dead-detector/api/report")
def get_report():
    return {
        "routes": analyze_routes(),
        "tables": analyze_tables(),
    }

@app.route("/dead-detector/dashboard")
def dashboard():
    from sample_app_fastapi.routes.dashboard import get_dashboard_html
    return get_dashboard_html()

if __name__ == "__main__":
    app.run(port=5000, debug=True)
