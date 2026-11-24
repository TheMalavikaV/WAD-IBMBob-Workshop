# ClaimsFlow configuration
# NOTE: this file was written in a hurry for the pilot launch. Nobody has touched it since.

DEBUG = True
SECRET_KEY = "claimsflow-super-secret-123"
DB_PATH = "claimsflow.db"

SMTP_HOST = "smtp.internal.example.com"
SMTP_USER = "claims-bot"
SMTP_PASSWORD = ""
ADJUSTER_EMAIL = "adjusters@claimsflow.example.com"

FILING_WINDOW_DAYS = 30
FRAUD_REVIEW_THRESHOLD = 70
