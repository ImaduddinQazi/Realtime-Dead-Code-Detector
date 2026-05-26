# Realtime-Dead-Code-Detector
In Development ⬆️

Runtime-based dead code detection system that silently instruments Python web applications (FastAPI, Flask, Django) via pluggable middleware, tracking every API call and database query without modifying application logic

### basic structure with sample project (your project)
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
