import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from project root
load_dotenv(Path(__file__).parent / ".env")

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

SECRET_KEY = os.getenv("SECRET_KEY", "fallback-secret-key-change-me")

DATABASE_PATH = os.getenv(
    "DATABASE_PATH",
    os.path.join(BASE_DIR, "database", "finance.db")
)

# ─────────────────────────────────────────────────
# 🔑 ADMIN ACCESS
# Set ADMIN_EMAILS in your .env file as a
# comma-separated list:
#   ADMIN_EMAILS=you@email.com,other@email.com
# ─────────────────────────────────────────────────
_raw_admin_emails = os.getenv("ADMIN_EMAILS", "")
ADMIN_EMAILS = [e.strip() for e in _raw_admin_emails.split(",") if e.strip()]
