# API Tests Documentation

## Overview

This directory contains API tests for the Trail Planner API. All tests have been updated to match the new database schema and include comprehensive tests for all endpoints.

## Configuration

Before running tests, update the `config.py` file with your API Gateway details:

- **BASE_URL**: Your API Gateway base URL (get from `terraform output api_gateway_url`)
- **COGNITO_TOKEN**: Your Cognito JWT token for authenticated endpoints
  - **Steps to retrieve**
  -  Log in to application via frontend
  -  Open "Inspect Element" and navigate to Application
  -  Navigate to "Session Storage"
  -  Click on "idToken" and select all (usually around 1080 characters)
- **API_KEY**: Your API key for the `/devices` endpoint

## Test Files

### Updated Tests (Existing Endpoints)

1. **test_PostOneData.py** → `test_post_trail_data_single()`
   - Tests POST `/trail_data` with a single data point
   - Uses schema: `trail_id`, `device_id`, `timestamp`, optional metrics
   - Uses Cognito authentication

2. **test_PostMultipleData.py** → `test_post_trail_data_multiple()`
   - Tests POST `/trail_data` with multiple data points in a batch
   - Updated to use new schema with proper data structure
   - Uses Cognito authentication

3. **test_GetAllTrailData.py** → `test_get_all_trail_data()`
   - Tests GET `/trail_data` to retrieve all trail device logs
   - Validates response structure matches new schema
   - Uses Cognito authentication

4. **test_GetOneTrail.py** → `test_get_trail_data_filtered()`
   - Tests GET `/trail_data` with query parameters
   - Updated to use `trails` parameter (comma-separated) instead of `trail`
   - Validates filtering by trail IDs
   - Uses Cognito authentication

### New Tests (Devices Endpoint)

5. **test_DevicesPost.py**
   - `test_post_device_data_success()`: Minimal payload POST to `/devices`
   - `test_post_device_data_with_additional_fields()`: POST with custom sensor fields
   - `test_post_device_data_batch_payload()`: Batched readings in one request
   - `test_post_device_data_multiple_devices()`: Multiple sequential requests
   - All use API key authentication

6. **test_DevicesPostValidation.py**
   - Covers missing/invalid API keys
   - Validates required `device_id`, `data`, and per-reading `ts`
   - Checks empty payloads, bad overrides, and malformed data

## Database Schema

All tests now use the updated database schema:

**Trail Device Logs:**
- `trail_id` (integer): Trail identifier (partition key)
- `timestamp` (integer): Unix epoch timestamp (sort key)
- `device_id` (string): Device identifier
- Optional attributes such as `battery` or other custom metrics submitted via `/trail_data`

**Devices Endpoint Payload:**
- Top-level `device_id` and optional `battery`
- `data`: list of entries each containing only `ts`
- Optional `trail_id` override; if omitted, server automatically determines trail from DeviceMetadata or previous logs (defaults to trail_id 1 for new devices)

## Running Tests

### Run All Tests
```bash
pytest completed/ -v
```

### Run Specific Test File
```bash
pytest completed/test_DevicesPost.py -v
```

### Run Tests with Markers
```bash
pytest completed/ -m API -v
```

### Run with Output
```bash
pytest completed/ -v -s
```

## Authentication

### Cognito Authentication
Used for `/trail_data` endpoints:
- Header: `Authorization: Bearer {cognito_jwt_token}`
- Token expires - update in `config.py` when needed

### API Key Authentication
Used for `/devices` endpoint:
- Header: `X-Api-Key: {api_key}`

## Test Coverage

- POST `/trail_data` (single and batch)
- GET `/trail_data` (all and filtered)
- POST `/devices` (success cases)
- POST `/devices` (validation/error cases)
- Authentication (Cognito and API key)
- Response structure validation
- Error handling validation

## Notes

- Tests generate unique timestamps to avoid conflicts
- Device IDs use test prefixes (`test_device_*`) for easy identification
- Some tests may fail if Cognito token expires - update in `config.py`
- API key is hardcoded in Terraform - update if changed

