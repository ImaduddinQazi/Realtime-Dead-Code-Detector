import re
from sqlalchemy import event
from sqlalchemy.engine import Engine
from database import SessionLocal
from models import DbTableUsage

IGNORED_TABLES = {"api_usage_logs", "db_table_usage"}

def extract_tables(statement):
    # Finds all table names after FROM or JOIN keywords
    return re.findall(
        r'\bFROM\s+"?(\w+)"?|\bJOIN\s+"?(\w+)"?',
        statement,
        re.IGNORECASE
    )

@event.listens_for(Engine, "before_cursor_execute")
def track_query(conn, cursor, statement, parameters, context, executemany):
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