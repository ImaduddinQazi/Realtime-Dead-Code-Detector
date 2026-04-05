from datetime import datetime, timezone
from database import SessionLocal
from models import ApiUsageLog
from sqlalchemy import func

# All routes registered in your app
# In Phase 4 we'll auto-discover these — hardcode for now
ALL_ROUTES = [
    ("GET",  "/users"),
    ("POST", "/users"),
    ("GET",  "/orders"),
    ("POST", "/orders/{order_id}/confirm"),
    ("GET",  "/v1/old-payment"),
    ("POST", "/v1/legacy-signup"),
]

ALL_TABLES = ["users", "orders", "legacy_payments"]

def calculate_confidence(last_seen_days, total_calls):
    """
    Confidence that an endpoint is DEAD (0-100%).
    Higher = more likely dead.
    """
    if total_calls == 0:
        return 97  # never called = almost certainly dead

    # Recency score: the older the last call, the higher the score
    if last_seen_days <= 1:
        recency = 0
    elif last_seen_days <= 7:
        recency = 30
    elif last_seen_days <= 14:
        recency = 55
    elif last_seen_days <= 30:
        recency = 75
    else:
        recency = 90

    # Frequency score: very low call count raises suspicion
    if total_calls > 100:
        frequency = 0
    elif total_calls > 20:
        frequency = 10
    elif total_calls > 5:
        frequency = 25
    else:
        frequency = 40

    return min(recency + frequency, 96)  # cap at 96% if ever called

def get_status(confidence):
    if confidence >= 80:
        return "DEAD"
    elif confidence >= 40:
        return "WARN"
    else:
        return "ACTIVE"

def analyze_routes():
    db = SessionLocal()
    results = []

    try:
        for method, path in ALL_ROUTES:
            # Count total calls
            total = db.query(func.count(ApiUsageLog.id))\
                .filter(ApiUsageLog.method == method)\
                .filter(ApiUsageLog.path == path)\
                .scalar()

            # Get last seen timestamp
            last_log = db.query(ApiUsageLog)\
                .filter(ApiUsageLog.method == method)\
                .filter(ApiUsageLog.path == path)\
                .order_by(ApiUsageLog.timestamp.desc())\
                .first()

            if last_log:
                now = datetime.now(timezone.utc)
                last_seen = last_log.timestamp.replace(tzinfo=timezone.utc)
                days_ago = (now - last_seen).days
                last_seen_str = last_log.timestamp.strftime("%Y-%m-%d %H:%M")
            else:
                days_ago = 9999
                last_seen_str = "never"

            confidence = calculate_confidence(days_ago, total)
            status = get_status(confidence)

            results.append({
                "method": method,
                "path": path,
                "total_calls": total,
                "last_seen": last_seen_str,
                "days_inactive": days_ago if days_ago != 9999 else None,
                "confidence": confidence,
                "status": status,
            })

    finally:
        db.close()

    # Sort: dead first, then warn, then active
    order = {"DEAD": 0, "WARN": 1, "ACTIVE": 2}
    results.sort(key=lambda x: order[x["status"]])
    return results

def analyze_tables():
    db = SessionLocal()
    results = []

    try:
        from models import DbTableUsage
        for table in ALL_TABLES:
            total = db.query(func.count(DbTableUsage.id))\
                .filter(DbTableUsage.table_name == table)\
                .scalar()

            last_log = db.query(DbTableUsage)\
                .filter(DbTableUsage.table_name == table)\
                .order_by(DbTableUsage.timestamp.desc())\
                .first()

            if last_log:
                now = datetime.now(timezone.utc)
                last_seen = last_log.timestamp.replace(tzinfo=timezone.utc)
                days_ago = (now - last_seen).days
                last_seen_str = last_log.timestamp.strftime("%Y-%m-%d %H:%M")
            else:
                days_ago = 9999
                last_seen_str = "never"

            confidence = calculate_confidence(days_ago, total)
            status = get_status(confidence)

            results.append({
                "table": table,
                "total_hits": total,
                "last_seen": last_seen_str,
                "confidence": confidence,
                "status": status,
            })

    finally:
        db.close()

    order = {"DEAD": 0, "WARN": 1, "ACTIVE": 2}
    results.sort(key=lambda x: order[x["status"]])
    return results