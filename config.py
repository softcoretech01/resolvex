import os

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "187.127.131.38"),
    "port": int(os.getenv("DB_PORT", 3310)),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASS", "ResolveX_Pass#2026"),
    "database": os.getenv("DB_NAME", "support_tool"),
    "autocommit": True
}