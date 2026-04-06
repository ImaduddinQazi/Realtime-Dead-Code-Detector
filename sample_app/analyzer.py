from datetime import datetime, timezone
from database import SessionLocal
from models import ApiUsageLog, DbTableUsage
from sqlalchemy import func
import re

ALL_ROUTES = [
    ("GET",  "/users"),
    ("POST", "/users"),
    ("GET",  "/orders"),
    ("POST", "/orders/{order_id}/confirm"),
    ("GET",  "/v1/old-payment"),
    ("POST", "/v1/legacy-signup"),
]

ALL_TABLES = ["users", "orders", "legacy_payments"]

def route_to_pattern(path):
    """Convert /orders/{order_id}/confirm → regex ^/orders/[^/]+/confirm$"""
    pattern = re.sub(r"\{[^}]+\}", r"[^/]+", path)
    pattern = pattern.rstrip("/")
    return re.compile(f"^{pattern}/?$")

def match_route(method, template_method, template_path, logged_paths):
    """Count how many logged paths match this route template."""
    if method != template_method:
        return 0
    pattern = route_to_pattern(template_path)
    return sum(1 for p in logged_paths if pattern.match(p))

def calculate_confidence(last_seen_days, total_calls):
    if total_calls == 0:
        return 97
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

    if total_calls > 100:
        frequency = 0
    elif total_calls > 20:
        frequency = 10
    elif total_calls > 5:
        frequency = 25
    else:
        frequency = 40

    return min(recency + frequency, 96)

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
        # Load all logs once — method + path per row
        all_logs = db.query(ApiUsageLog).all()

        for method, path in ALL_ROUTES:
            # Find all logs matching this route template
            pattern = route_to_pattern(path)
            matching_logs = [
                log for log in all_logs
                if log.method == method and pattern.match(log.path)
            ]

            total = len(matching_logs)

            if matching_logs:
                latest = max(matching_logs, key=lambda l: l.timestamp)
                now = datetime.now(timezone.utc)
                last_seen = latest.timestamp.replace(tzinfo=timezone.utc)
                days_ago = (now - last_seen).days
                last_seen_str = latest.timestamp.strftime("%Y-%m-%d %H:%M")
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

    order = {"DEAD": 0, "WARN": 1, "ACTIVE": 2}
    results.sort(key=lambda x: order[x["status"]])
    return results

def analyze_tables():
    db = SessionLocal()
    results = []

    try:
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