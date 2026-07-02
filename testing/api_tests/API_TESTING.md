# API Tests Documentation

## Overview

This directory contains API tests for the Trail Count API. All tests have been updated to match the new database schema and include comprehensive tests for all endpoints. The general purpose testing documentation can be found in [TESTING_OVERVIEW](../TESTING_OVERVIEW.md.).

## Prerequisites

### Required Packages

Follow the prerequisites outlined in [TESTING_OVERVIEW](../TESTING_OVERVIEW.md.).

## Configuration

Configuration is automatically determined from the `tests/.env` file, more information in [TESTING_OVERVIEW](../TESTING_OVERVIEW.md.).

## Running Tests

Information about running tests in [TESTING_OVERVIEW](../TESTING_OVERVIEW.md.).

## Test Files

### Old Tests

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

## Authentication

Endpoints are authenticated in two ways, a custom lambda authorizer and an api key (soon to be mTLS encryption). More information on each authentication method and which endpoints use what can be found in [API_DOCUMENTATION.md](../../API_DOCUMENTATION.md)

## Test Coverage

- POST `/trail_data` (single and batch)
- GET `/trail_data` (all and filtered)
- POST `/devices` (success cases)
- POST `/devices` (validation/error cases)
- Authentication (Cognito and API key)
- Response structure validation
- Error handling validation