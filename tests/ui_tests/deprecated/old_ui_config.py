"""
Configuration file for UI tests.
Update these values to match your deployment.
"""

# Base URL of the application
# Update this with your actual S3 bucket website URL
BASE_URL = ""

# Login credentials
LOGIN_EMAIL = "admin@gmail.com"
LOGIN_PASSWORD = "password"

# Wait times (in seconds)
DEFAULT_WAIT_TIME = 10
SHORT_WAIT_TIME = 2
MEDIUM_WAIT_TIME = 3
LONG_WAIT_TIME = 5

# Test data
DEFAULT_START_DATE = "01/01/2025"
DEFAULT_END_DATE = "12/01/2025"
TEST_START_DATE = "06/01/2025"
TEST_END_DATE = "12/01/2025"

# Element selectors (for consistency)
EMAIL_FIELD_ID = "email"
PASSWORD_FIELD_ID = "password"
SIGN_IN_BUTTON_CLASS = "button-3d"
LOGOUT_BUTTON_CLASS = "logout-button"
START_DATE_CLASS = "date-picker-start-date"
END_DATE_CLASS = "date-picker-end-date"
TRAIL_SELECTOR_CLASS = "trail-selector"
GRANULARITY_ID = "granularity"
FILTER_CONTAINER_CLASS = "filter-container"