import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")

# Base URL of the application
BASE_URL = os.getenv("CLOUDFRONT_URL")

# Passwords for premade accounts
USER_PASSWORDS = os.getenv("USER_PASSWORDS")

# Whether run is local (Headless or not)
LOCAL_RUN = os.getenv("LOCAL_RUN") == "true"