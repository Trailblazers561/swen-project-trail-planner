"""
Configuration file for API tests.
Update these values to match your API Gateway deployment.
"""

# Base URL of the API Gateway
# Update this with your actual API Gateway URL from: terraform output api_gateway_url
BASE_URL = ""

# Cognito JWT Token for authenticated endpoints
# This token will expire - update it when needed
COGNITO_TOKEN = ""

# API Key for /devices endpoint
API_KEY = ""

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

