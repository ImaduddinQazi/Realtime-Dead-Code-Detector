import re
from sqlalchemy import event
from sqlalchemy.engine import Engine
from database import SessionLocal
from models import DbTableUsage

IGNORED_TABLES = {"api_usage_logs", "db_table_usage", "pg_catalog", "pg_class", "pg_namespace"}

_tables_ready = False  # ← guard flag

def set_tables_ready():
    global _tables_ready
    _tables_ready = True

def extract_tables(statement):
    return re.findall(
        r'\bFROM\s+"?(\w+)"?|\bJOIN\s+"?(\w+)"?',
        statement,
        re.IGNORECASE
    )

@event.listens_for(Engine, "before_cursor_execute")
def track_query(conn, cursor, statement, parameters, context, executemany):
    if not _tables_ready:  # ← skip if tables don't exist yet
        return

    matches = extract_tables(statement)
    tables = set()
    for match in matches:
        tables.update(t for t in match if t)

    tables -= IGNORED_TABLES
    if not tables:
        return

    db = SessionLocal()
    try:
        for table in tables:
            db.add(DbTableUsage(table_name=table))
        db.commit()
    finally:
        db.close()