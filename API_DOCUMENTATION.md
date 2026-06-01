# Trail Count API Documentation

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

The public API also uses a custom domain for the main environments. The format is:
```
https://trailblazers-public-api-<deploy_env>.adirondackwilderness.org
```

## Authentication

The API uses two authentication methods depending on the endpoint:

### 1. Custom Lambda Authorizer Authentication
Most endpoints require a Cognito JWT access token in the `Authorization` header.

**Header Format:**
```
Authorization: Bearer {cognito_jwt_token}
```

**How to obtain a token:**
- Using AWS Cognito authentication flow (Sign In, Sign Up, etc.)
  - **Steps to retrieve**
  -  Log in to application via frontend
  -  Open "Inspect Element" and navigate to Application
  -  Navigate to "Session Storage"
  -  Click on "idToken" and select all (usually around 1080 characters)
- Using command line
  - **Steps to retrieve**
  - Ensure you have setup `aws configure` for an account that matches the one with the deployment
  - Determine the cognito client id
  - Run the following command, append ` --output json > token.json` to store the output into a json file
  - ```aws cognito-idp initiate-auth --region us-east-1 --auth-flow USER_PASSWORD_AUTH --client-id <CLIENT_ID> --auth-parameters USERNAME=<USERNAME>,PASSWORD=<PASSWORD>```

### 2. API Key Authentication
The `/devices` endpoint uses standard cognito authentication, not an API key. This will eventually be changed to mTLS authentication and put onto a different api.

**Header Format:**
```
X-Api-Key: {aws_api_key}
```

**Usage Plan Limits:**
- Rate Limit: 50 requests per second
- Burst Limit: 100 requests
- Daily Quota: 10,000 requests per day
 > **Note**: The usage plan limits can be changed depending on needs in `public_api.tf` under `device_usage_plan`

---

## Endpoints

### Register Device

Register a device to the system. Devices must be registered before being used, and then associated to a trail before any other actions. This endpoint is designed for device-to-cloud communication.

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
  "name": "sample_name",
  "firmware_version": "1.0.0",
  "manufacture_timestamp": 1767243600,
  "notes": "sample notes go here"
}
```

**Required Fields:**
- `name` (string): The name of the device to register, usually the devices hashed mac address. Cannot be updated.
- `firmware_version` (string): The current version of the firmware on the device. Can be updated later.
- `manufacture_timestamp` (int): A timestamp of when the device was created. Cannot be updated.

**Optional Fields:**
- `notes` (string): Notes associated with the given device. Can be updated later.

**Success Response (200 OK):**
```json
{
  "message": "Device created successfully",
  "device_id": 1
}
```

### Upload Device Data

Used to upload timestamps from the device and updated various information regarding the device. This endpoint is designed for device-to-cloud communication.

**Endpoint:** `PUT /devices`

**Authentication:** API Key (required)

**Headers:**
```
X-Api-Key: {aws_api_key}
Content-Type: application/json
```

**Request Body:**
```json
{
  "name": "sample_name",
  "data": [
    {"timestamp": 1767243600, "count": 184}
  ],
  "battery": 94,
  "firmware_version": "1.0.0",
  "notes": "sample notes go here",
  "errors": [
    {"timestamp": 1767243600, "error": "This error happened"}
  ]
}
```

**Required Fields:**
- `name` (string): The name of the device to upload data to, usually the devices hashed mac address.

**Optional Fields:**
- `data` (array): An array of timestamped counts to upload.
  - `timestamp` (int): The timestamp for the start of the count, should ideally be lined up to the start of the hour, should always represent an hour worth of counts.
  - `count` (int): The amount of hikers counted during the hour starting at the provided timestamp.
- `battery` (int): The current battery percentage of the device when the counts are sent in. Should always be provided with `data`.
- `firmware_version` (string): The current version of the firmware on the device. Device firmware_version will be updated if this is sent.
- `notes` (string): Notes associated with the given device. Device notes will be updated if this is sent.
- `errors` (array): An array of timestamped errors to upload.
  - `timestamp` (int): The timestamp that the error occurred.
  - `error` (string): A string providing information on the error that occurred. Ideally it is error name followed by error description.
- At least one optional field should be present (`data`/`battery`, `firmware_version`, `notes`, `errors`).

**Success Response (200 OK):**
```json
{
  "message": ["Firmware version updated successfully", "Device data uploaded successfully"]
}
```


### Get Device Metadata

Retrieves metadata for the devices, as well as appending additional fields `trail_id`, `notes`, `date_installed`, and `date_removed`. This endpoint is designed for cloud-to-cloud communication.

**Endpoint:** `GET /device_metadata`

**Authentication:** Cognito JWT Access Token (required)

**Headers:**
```
Authorization: Bearer {cognito_jwt_token}
Content-Type: application/json
```

**Query Parameters:**
- `device_id` (optional, "int"): Specific device id to retrieve metadata from, can be specified multiple times eg. (?device_id=1&device_id=2).

**Success Response (200 OK):**
```json
{
  [
    {
      "id": 1,
      "name": "sample_name",
      "firmware_version": "1.0.0",
      "notes": "sample_notes",
      "date_manufactured": 1767243600,
      "current_trail_id": 1,
      "trail_history": [
        {
          "trail_id": 1,
          "date_installed": 1767243600,
          "notes": "sample_device_trail_notes"
        }
      ]
    }      
  ]
}
```

### Update Device Trail Association

Updates the device trail association for the provided device and trail. Will retire any existing device trail associations with the given device or trail before creating a new association. This endpoint is designed for cloud-to-cloud communication.

**Endpoint:** `PUT /device_metadata`

**Authentication:** Cognito JWT Access Token (required)

**Headers:**
```
Authorization: Bearer {cognito_jwt_token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "device_id": 1,
  "trail_id": 1,
  "date_installed": "2026-01-01",
  "date_removed": "2026-01-01"
}
```

**Required Fields:**
- `device_id` (int): Id of the device to associate.
- `trail_id` (int): Id of the trail to associate.

**Optional Fields:**
- `date_installed` (string): ISO format date for when the new device was installed on the trail, defaults to time of request.
- `date_removed` (string): ISO format date for when the old device was removed from the trail, defaults to time of request.

**Success Response (200 OK):**
```json
{
  "message": "Device trail association updated successfully"
}
```


### Get Trail Metadata

Retrieves metadata for the trails. This endpoint is designed for cloud-to-cloud communication.

**Endpoint:** `GET /trail_metadata`

**Authentication:** Cognito JWT Access Token (required)

**Headers:**
```
Authorization: Bearer {cognito_jwt_token}
Content-Type: application/json
```

**Query Parameters:**
- `trail_id` (optional, "int"): Specific trail id to retrieve metadata from, can be specified multiple times eg. (?trail_id=1&trail_id=2).

**Success Response (200 OK):**
```json
{
  [
    {
      "id": 1,
      "name": "sample_name",
      "notes": "sample_notes",
      "latitude": 43.0847,
      "longitude": 77.6715,
      "date_activated": "2026-01-01",
      "date_retired": "2026-12-31"
    }
  ]
}
```

### Create Trail

Creates a trail with the provided information. This endpoint is designed for cloud-to-cloud communication.

**Endpoint:** `POST /trail_metadata`

**Authentication:** Cognito JWT Access Token (required)

**Headers:**
```
Authorization: Bearer {cognito_jwt_token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "name": "sample_name",
  "area_name": "sample_area",
  "notes": "sample_notes",
  "latitude": 43.0847,
  "longitude": 77.6715,
  "date_activated": "2026-01-01"
}
```

**Required Fields:**
- `name` (string): Name of the trail to create. Can be updated later.

**Optional Fields:**
- `area_name` (string): Name of the area to put the new trail in. Can be updated later.
- `notes` (string): Notes associated with the given trail. Can be updated later.
- `latitude` (float): Latitude coordinate for the head of the trail, or where the device would be placed. Can be updated later.
- `longitude` (float): Longitude coordinate for the head of the trail, or where the device would be placed. Can be updated later.
- `date_activated` (string): ISO format date for when the trail was activated or created, defaults to time of request. Cannot be updated.

**Success Response (200 OK):**
```json
{
  "message": "Trail created successfully",
  "trail_id": 1
}
```

### Update Trail Metadata

Updates a specific trail with the provided information. This endpoint is designed for cloud-to-cloud communication.

**Endpoint:** `PUT /trail_metadata`

**Authentication:** Cognito JWT Access Token (required)

**Headers:**
```
Authorization: Bearer {cognito_jwt_token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "trail_id": 1,
  "name": "sample_name",
  "area_name": "sample_area",
  "notes": "sample_notes",
  "latitude": 43.0847,
  "longitude": 77.6715
}
```

**Required Fields:**
- `trail_id` (int): Id for the trail to update.

**Optional Fields:**
- `name` (string): Name of the trail.
- `area_name` (string): Name of the area to put the trail in.
- `notes` (string): Notes associated with the given trail.
- `latitude` (float): Latitude coordinate for the head of the trail, or where the device would be placed.
- `longitude` (float): Longitude coordinate for the head of the trail, or where the device would be placed.

**Success Response (200 OK):**
```json
{
  "message": "Trail metadata updated successfully"
}
```

### Retire Trail

Retires the given trail Retired trails will not appear when retrieving all trails, but information with them can be retrieved when their trail id is specified. This endpoint is designed for cloud-to-cloud communication.

**Endpoint:** `DELETE /trail_metadata`

**Authentication:** Cognito JWT Access Token (required)

**Headers:**
```
Authorization: Bearer {cognito_jwt_token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "trail_id": 1,
  "date_retired": "2026-12-31"
}
```

**Required Fields:**
- `trail_id` (int): Id of the trail to retire.

**Optional Fields:**
- `date_retired` (string): ISO format date for when to set the date_retired of the trail. Defaults to time of request.

**Success Response (200 OK):**
```json
{
  "message": "Trail and all associated data retired successfully"
}
```


### Get Area Metadata

Retrieves metadata for the areas. This endpoint is designed for cloud-to-cloud communication.

**Endpoint:** `GET /areas`

**Authentication:** Cognito JWT Access Token (required)

**Headers:**
```
Authorization: Bearer {cognito_jwt_token}
Content-Type: application/json
```

**Query Parameters:**
- `area` (optional, "str"): Specific area name to retrieve metadata from, can be specified multiple times eg. (?area=Adirondack%20Park&area=High%20Peaks%20Wilderness).

**Success Response (200 OK):**
```json
{
  [
    {
      "name": "sample_name",
      "trail_ids": [1, 2]
    }
  ]
}
```

### Delete Area

Deletes the specified area. This endpoint is designed for cloud-to-cloud communication.

**Endpoint:** `DELETE /areas`

**Authentication:** Cognito JWT Access Token (required)

**Headers:**
```
Authorization: Bearer {cognito_jwt_token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "name": "sample_name"
}
```

**Required Fields:**
- `name` (string): Name of the area to delete.

**Success Response (200 OK):**
```json
{
  "message": "Area deleted successfully"
}
```


### Get Trail Device Logs

Retrieves the trail device logs for the specified trails, between the specified dates. This endpoint is designed for cloud-to-cloud communication.

**Endpoint:** `GET /trail_data`

**Authentication:** Cognito JWT Access Token (required)

**Headers:**
```
Authorization: Bearer {cognito_jwt_token}
Content-Type: application/json
```

**Query Parameters:**
- `trail_id` ("int"): Specific trail id to retrieve logs of, can be specified multiple times eg. (?trail_id=1&trail_id=2).
- `start_time` (string): ISO format string for the earliest date to retrieve logs from.
- `end_time` (string): ISO format string for the latest date to retrieve logs from.
- `granularity` (optional, string): Granularity of the logs to retrieve, defaults to _day_. Valid options are _hour_, _day_, _week_, and _month_.

**Success Response (200 OK):**
```json
{
  [
    {
      "trail_id": 1,
      "device_id": 1,
      "device_trail_id": 1,
      "start": 1767243600,
      "count": 493,
      "battery": 96
    }
  ]
}
```

### Upload Trail Data

Uploads trail timestamp counts, also automatically called when devices upload data to handle device trail data upload. This endpoint is designed for cloud-to-cloud communication.

**Endpoint:** `POST /trail_data`

**Authentication:** Cognito JWT Access Token (required)

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
    {"timestamp": 1767243600, "count": 184}
  ],
  "battery": 96
}
```

**Required Fields:**
- `trail_id` (int): The id of the trail to upload data to.
- `data` (array): An array of timestamped counts to upload.
  - `timestamp` (int): The timestamp for the start of the count, should ideally be lined up to the start of the hour, should always represent an hour worth of counts.
  - `count` (int): The amount of hikers counted during the hour starting at the provided timestamp.
- `battery` (int): The current battery percentage of the device when the counts are sent in.

**Success Response (200 OK):**
```json
{
  "message": "Trail data uploaded"
}
```


### Export CSV

Generates a csv for the given trails, between the given dates. Returns a url that can be used to download the csv. This endpoint is designed for cloud-to-cloud communication.

**Endpoint:** `GET /csv`

**Authentication:** Cognito JWT Access Token (required)

**Headers:**
```
Authorization: Bearer {cognito_jwt_token}
Content-Type: application/json
```

**Query Parameters:**
- `trail_id` ("int"): Specific trail id to retrieve logs of, can be specified multiple times eg. (?trail_id=1&trail_id=2).
- `start_time` (string): ISO format string for the earliest date to retrieve logs from.
- `end_time` (string): ISO format string for the latest date to retrieve logs from.
- `granularity` (optional, string): Granularity of the logs to retrieve, defaults to _day_. Valid options are _hour_, _day_, _week_, and _month_.

**Success Response (200 OK):**
```json
{
  "url": "sample_download_url"
}
```

### Import CSV

Reads a csv and imports the data within it into the database. CSV must first be uploaded to a url retrieved with Get Import CSV Upload Link. This endpoint is designed for cloud-to-cloud communication.

**Endpoint:** `POST /csv`

**Authentication:** Cognito JWT Access Token (required)

**Headers:**
```
Authorization: Bearer {cognito_jwt_token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "csv_file_path": "tmp-upload/sample_hash/trail_data.csv"
}
```

**Required Fields:**
- `csv_file_path` (string): The file path that the import csv file was uploaded to.

**Success Response (200 OK):**
```json
{
  "importSuccess": true
}
```

### Get Import CSV Upload Link

Retrieves a link that can be used to upload a csv file to. This endpoint is designed for cloud-to-cloud communication.

**Endpoint:** `GET /csv-url`

**Authentication:** Cognito JWT Access Token (required)

**Headers:**
```
Authorization: Bearer {cognito_jwt_token}
Content-Type: application/json
```

**Success Response (200 OK):**
```json
{
  "uploadURL": "sample_upload_url",
  "s3FilePath": "sample_file_path"
}
```


### Get Users

Retrieves a list of registered cognito users. This endpoint is designed for cloud-to-cloud communication.

**Endpoint:** `GET /users`

**Authentication:** Cognito JWT Access Token (required)

**Headers:**
```
Authorization: Bearer {cognito_jwt_token}
Content-Type: application/json
```

**Query Parameters:**
- `target_user_role` (optional, string): The minimum role to search within, will return users with at least the provided role. Valid options are _user_, _trail_manager_, _admin_, _root_admin_.
- `max_count` (optional, "int"): The maximum amount of users to retrieve, defaults to 99.

**Success Response (200 OK):**
```json
{
  [
    {
      "user_id": "sample_user_id",
      "username": "sample_username",
      "email": "sample_email",
      "first_name": "sample_first_name",
      "last_name": "sample_last_name"
    }
  ]
}
```

### Change User Role

Updates the role of the specified cognito user to the specified role. This endpoint is designed for cloud-to-cloud communication.

**Endpoint:** `POST /users`

**Authentication:** Cognito JWT Access Token (required)

**Headers:**
```
Authorization: Bearer {cognito_jwt_token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "target_user_id": "example_user_id",
  "target_user_role": "admin"
}
```

**Required Fields:**
- `target_user_id` (string): The id for the user whose role is going to be updated.
- `target_user_role` (type): The role to set the specified user to. Valid options are _user_, _trail_manager_, _admin_.

**Success Response (200 OK):**
```json
{
  "message": "User groups updated"
}
```

## Rate Limiting

### API Key Endpoints (`/devices`)
- **Rate Limit:** 50 requests per second
- **Burst Limit:** 100 requests
- **Daily Quota:** 10,000 requests per day

When rate limits are exceeded, you will receive a `429 Too Many Requests` response.
 > **Note**: The usage plan limits can be changed depending on needs in `public_api.tf` under `device_usage_plan`

### Cognito Authenticated Endpoints
Rate limits are determined by AWS API Gateway default limits and your AWS account configuration.