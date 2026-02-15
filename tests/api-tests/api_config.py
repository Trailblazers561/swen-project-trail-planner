"""
Configuration file for API tests.
Update these values to match your deployment.
"""
import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")

# Base URL of the API Gateway
BASE_URL = os.getenv("API_URL")

# Cognito JWT Token for authenticated endpoints
# This token will expire - update it when needed
COGNITO_TOKEN = os.getenv("API_TOKEN")

# API Key for /devices endpoint
API_KEY = os.getenv("API_KEY")

print("THHINGS: ", BASE_URL, API_KEY, COGNITO_TOKEN)

# Headers for Cognito-authenticated requests
def get_cognito_headers():
    return {
        "Authorization": f"Bearer {COGNITO_TOKEN}",
        "Content-Type": "application/json"
    }

# Headers for API key-authenticated requests
def get_api_key_headers():
    return {
        "X-Api-Key": API_KEY,
        "Content-Type": "application/json"
    }

