# Trail Planner API Documentation

## Base URL

The API base URL is provided by the Terraform output `api_gateway_url`. The format is:
```
https://{api-id}.execute-api.{region}.amazonaws.com/{stage}
```

To get the API URL, run:
```bash
terraform output api_gateway_url
```

---

## Authentication

The API uses two authentication methods depending on the endpoint:

### 1. Cognito User Pool Authentication
Most endpoints require a Cognito JWT token in the `Authorization` header.

**Header Format:**
```
Authorization: Bearer {cognito_jwt_token}
```

**How to obtain a token:**
- Use AWS Cognito authentication flow (Sign In, Sign Up, etc.)
  - **Steps to retrieve**
  -  Log in to application via frontend
  -  Open "Inspect Element" and navigate to Application
  -  Navigate to "Session Storage"
  -  Click on "idToken" and select all (usually around 1080 characters)
- The token is typically obtained after user login through the frontend application

### 2. API Key Authentication
The `/devices` endpoint requires an API key in the request header.

**Header Format:**
```
X-Api-Key: {aws_api_key}
```

Please note that the default API key is `MSD-24572-TRAIL-PLANNER-KEY`. This can be changed in `api.tf`

**Usage Plan Limits:**
- Rate Limit: 50 requests per second
- Burst Limit: 100 requests
- Daily Quota: 10,000 requests per day
 > **Note**: The usage plan limits can be changed depending on needs in `api.tf` under `device_usage_plan`

---

## Endpoints

### 1. Upload Device Data

Upload trail data from IoT devices. This endpoint is designed for device-to-cloud communication with minimal payload size.

**Endpoint:** `POST /devices`

**Authentication:** API Key (required)

**Headers:**
```
X-Api-Key: {aws_api_key}
Content-Type: application/json
```

**Request Body:**
```json
{
  "device_id": "deviceA",
  "battery": 95,
  "data": [
    { "ts": 1759064864 },
    { "ts": 1759064924 }
  ]
}
```

**Required Fields:**
- `device_id` (string or number): Unique identifier for the device
- `data` (array): At least one reading
- Each reading must include only `ts` (integer Unix epoch); no other per-reading fields are accepted.

**Optional Fields:**
- `battery` (number): Device battery level applied to all readings in this request
- `trail_id` (integer): Optional override; if omitted, the server automatically determines the trail using:
  1. DeviceMetadata table (if device was previously registered)
  2. Most recent entry in TrailDeviceLogs for that device
  3. Default trail_id 0 for brand new devices

**Automatic Trail Resolution:**
- The server automatically links devices to trails without requiring manual registration
- On first use, new devices default to trail_id 0
- The server caches the trail assignment in DeviceMetadata for faster future lookups
- If a device moves to a new trail, include `trail_id` in the payload to update the assignment

**`/devices/` Filtering**
- Any POST request to `/devices/` has the following limitations
  - Duplicate timestamps from the **same** device are ignored
  - Timestamps from before 1735707600 (January 1, 2025) are **ignored**
    - This is due to the device sometimes sending 946702800 (January 1, 2000) timestamps

**Success Response (200 OK):**
```json
{
  "message": "Device data uploaded successfully"
}
```

**Error Responses:**

**400 Bad Request** - Missing required fields:
```json
{
  "error": "Missing required fields: device_id, data"
}
```

**400 Bad Request** - Invalid data format:
```json
{
  "error": "Invalid data format: {error_details}"
}
```

**403 Forbidden** - Missing or invalid API key:
```
{
  "message": "Forbidden"
}
```

**500 Internal Server Error:**
```json
{
  "error": "Internal server error: {error_details}"
}
```

**Example cURL:**
```bash
curl -X POST https://{api-url}/devices \
  -H "X-Api-Key: {aws_api_key}" \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "deviceA",
    "battery": 95,
    "data": [
      { "ts": 1759064864 },
      { "ts": 1759064924 }
    ]
  }'
```

---

### 2. Get Trail Data

Retrieve trail device logs. Can filter by specific trails or retrieve all logs.

**Endpoint:** `GET /trail_data`

**Authentication:** Cognito JWT Token (required)

**Headers:**
```
Authorization: Bearer {cognito_jwt_token}
Content-Type: application/json
```

**Query Parameters:**
- `trails` (optional, string): Comma-separated list of trail IDs to filter by (e.g., `trails=1,2,3`)
- `start` (optional, string): Start timestamp for filtering (not currently implemented in Lambda)
- `end` (optional, string): End timestamp for filtering (not currently implemented in Lambda)

**Request Examples:**

Get all trail data:
```
GET /trail_data
```

Get data for specific trails:
```
GET /trail_data?trails=1,2,3
```

Get data with date range (if implemented):
```
GET /trail_data?trails=1&start=1759064864&end=1759065000
```

**Success Response (200 OK):**
```json
[
  {
    "trail_id": 1,
    "device_id": "deviceA",
    "timestamp": 1759064864,
    "battery": 95
  },
  {
    "trail_id": 1,
    "device_id": "deviceA",
    "timestamp": 1759065044,
    "battery": 94
  }
]
```

**Error Responses:**

**401 Unauthorized** - Missing or invalid Cognito token:
```json
{
  "message": "Unauthorized"
}
```

**Example cURL:**
```bash
curl -X GET "https://{api-url}/trail_data?trails=1,2" \
  -H "Authorization: Bearer {cognito_jwt_token}" \
  -H "Content-Type: application/json"
```

---

### 3. Upload Trail Data

Upload multiple trail data points in a batch. Used for bulk data uploads from authenticated users.

**Endpoint:** `POST /trail_data`

**Authentication:** Cognito JWT Token (required)

**Headers:**
```
Authorization: Bearer {cognito_jwt_token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "trail_id": 1,
  "data": [
    {
      "device_id": "deviceA",
      "timestamp": 1759064864,
      "battery": 95
    },
    {
      "device_id": "deviceA",
      "timestamp": 1759065044,
      "battery": 94
    }
  ]
}
```

**Required Fields:**
- `trail_id` (integer): The ID of the trail
- `data` (array): Array of data points to upload

**Data Point Fields:**
- `device_id` (string): Required unique identifier
- `timestamp` (integer): Unix epoch timestamp
- Additional fields are optional and will be stored

**Success Response (200 OK):**
```json
{
  "message": "Trail data uploaded"
}
```

**Error Responses:**

**401 Unauthorized** - Missing or invalid Cognito token:
```json
{
  "message": "Unauthorized"
}
```

**Example cURL:**
```bash
curl -X POST https://{api-url}/trail_data \
  -H "Authorization: Bearer {cognito_jwt_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "trail_id": 1,
    "data": [
      {
        "device_id": "deviceA",
        "timestamp": 1759064864,
        "battery": 95
      }
    ]
  }'
```

## Data Models

### Trail Device Log Entry

Stored in the `TrailDeviceLogs` DynamoDB table.

**Primary Key:**
- `trail_id` (Number): Partition key
- `timestamp` (Number): Sort key

**Attributes:**
- `device_id` (String): Device identifier
- `battery` (Number, optional): Battery level
- Additional custom fields as needed

**Example:**
```json
{
  "trail_id": 1,
  "device_id": "deviceA",
  "timestamp": 1759064864,
  "battery": 95
}
```

---

## Rate Limiting

### API Key Endpoints (`/devices`)
- **Rate Limit:** 50 requests per second
- **Burst Limit:** 100 requests
- **Daily Quota:** 10,000 requests per day

When rate limits are exceeded, you will receive a `429 Too Many Requests` response.
 > **Note**: The usage plan limits can be changed depending on needs in `api.tf` under `device_usage_plan`

### Cognito Authenticated Endpoints
Rate limits are determined by AWS API Gateway default limits and your AWS account configuration.

---

## Notes

1. **Timestamp Format:** All timestamps should be Unix epoch integers (seconds since January 1, 1970 UTC) e.g. 1761793438

2. **Batch Operations:** Both `/devices` and `/trail_data` POST endpoints support batch uploads for efficient data ingestion.

3. **Query Filtering:** The `start` and `end` query parameters are accepted but not currently implemented in the Lambda function. They are reserved for future date range filtering functionality.

4. **Additional Fields:** Both `/devices` and `/trail_data` endpoints accept additional custom fields beyond the required ones. These will be stored in DynamoDB.

---