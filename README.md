# Realtime-Dead-Code-Detector
In Development ⬆️

A runtime-based dead code detector for FastAPI applications. It silently tracks which API endpoints and database tables are actually being used in production, and flags unused ones with a confidence score — so you know what's safe to delete.

### basic structure 
Realtime-Dead-Code-Detector/
└── sample_app/
    ├── main.py         
    ├── models.py
    ├── database.py
    ├── requirements.txt
    └── routes/
        ├── __init__.py
        ├── users.py
        ├── orders.py
        └── legacy.py
