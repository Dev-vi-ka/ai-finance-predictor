import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

SECRET_KEY = "super-secret-key-change-later"

DATABASE_PATH = os.path.join(BASE_DIR, "database", "finance.db")

# Admin Configuration
ADMIN_EMAILS = os.getenv('ADMIN_EMAILS', 'admin@finance.com').split(',')  # comma-separated list
ADMIN_EMAILS = [email.strip() for email in ADMIN_EMAILS]  # Remove whitespace
