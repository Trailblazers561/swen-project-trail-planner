# TABLE 1: TrailDeviceLogs
resource "aws_dynamodb_table" "trail_device_logs" {
  name         = "${local.name_prefix}TrailDeviceLogs"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "trail_id"
  range_key    = "timestamp"

  attribute {
    name = "trail_id"
    type = "N"
  }

  attribute {
    name = "timestamp"
    type = "N"
  }

  attribute {
    name = "device_id"
    type = "S"
  }

  global_secondary_index {
    name            = "device_id-timestamp-index"
    hash_key        = "device_id"
    range_key       = "timestamp"
    projection_type = "ALL"
  }

  tags = {
    Environment = "dev"
    TableType   = "Logs"
  }
}

# TABLE 2: DeviceMetadata
resource "aws_dynamodb_table" "device_metadata" {
  name           = "${local.name_prefix}DeviceMetadata"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "device_id"

  attribute {
    name = "device_id"
    type = "S"
  }

  tags = {
    Environment = "dev"
    TableType   = "Metadata"
  }
}

# TABLE 3: TrailMetadata
resource "aws_dynamodb_table" "trail_metadata" {
  name           = "${local.name_prefix}TrailMetadata"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "trail_id"

  attribute {
    name = "trail_id"
    type = "N"
  }

  attribute {
    name = "trail_name"
    type = "S"
  }

  global_secondary_index {
    name            = "trail_name-index"
    hash_key        = "trail_name"
    projection_type = "ALL"
  }

  tags = {
    Environment = "dev"
    TableType   = "TrailMetadata"
  }
}

# TABLE 4: DeviceCallLog
resource "aws_dynamodb_table" "device_call_log" {
  name         = "${local.name_prefix}DeviceCallLog"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "device_id"
  range_key    = "timestamp"

  attribute {
    name = "device_id"
    type = "S"
  }

  attribute {
    name = "timestamp"
    type = "N"
  }

  tags = {
    Environment = "dev"
    TableType   = "DeviceCallLog"
  }
}

# TABLE 5: TrailGroups
resource "aws_dynamodb_table" "trail_groups" {
  name           = "${local.name_prefix}TrailGroups"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "group_name"

  attribute {
    name = "group_name"
    type = "S"
  }

  tags = {
    Environment = "dev"
    TableType   = "TrailGroups"
  }
}

