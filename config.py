import os

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASS", "Bhava@303030"),
    "database": os.getenv("DB_NAME", "support_tool"),
    "autocommit": True
}
