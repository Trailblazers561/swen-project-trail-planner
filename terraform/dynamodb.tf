
# TABLE 1: TrailDeviceLogs
resource "aws_dynamodb_table" "trail_device_logs" {
  name           = "TrailDeviceLogs"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "trail_id"
  range_key      = "device_timestamp"

  attribute {
    name = "trail_id"
    type = "N"
  }

  attribute {
    name = "device_timestamp"
    type = "S"
  }

  attribute {
    name = "device_id"
    type = "S"
  }

  attribute {
    name = "timestamp"
    type = "N"
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
  name           = "DeviceMetadata"
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
  name           = "TrailMetadata"
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

# VARIABLES: SAMPLE DATA
variable "trail_device_logs_sampledata" {
  type = list(object({
    trail_id          = string
    device_timestamp  = string
    device_id         = string
    timestamp         = string
    battery           = string
  }))
  default = [
    {
      trail_id         = "1"
      device_timestamp = "deviceA#1704744000"
      device_id        = "deviceA"
      timestamp        = "1704744000"
      battery          = "95"
    },
    {
      trail_id         = "1"
      device_timestamp = "deviceA#1704747600"
      device_id        = "deviceA"
      timestamp        = "1704747600"
      battery          = "94"
    },
    {
      trail_id         = "2"
      device_timestamp = "deviceB#1704744000"
      device_id        = "deviceB"
      timestamp        = "1704744000"
      battery          = "88"
    }
  ]
}

variable "device_metadata_sampledata" {
  type = list(object({
    device_id         = string
    current_trail_id  = string
    battery           = string
    last_update       = string
  }))
  default = [
    {
      device_id        = "deviceA"
      current_trail_id = "1"
      battery          = "94"
      last_update      = "1704747600"
    },
    {
      device_id        = "deviceB"
      current_trail_id = "2"
      battery          = "88"
      last_update      = "1704744000"
    }
  ]
}

variable "trail_metadata_sampledata" {
  type = list(object({
    trail_id   = string
    trail_name = string
  }))
  default = [
    { trail_id = "1", trail_name = "Mt. Marcy" },
    { trail_id = "2", trail_name = "Wolf Creek Mountain" },
    { trail_id = "3", trail_name = "Mt. Joe" },
    { trail_id = "4", trail_name = "Mt. America" },
    { trail_id = "5", trail_name = "Blueberry Trail" },
    { trail_id = "6", trail_name = "Sunset Peak" },
    { trail_id = "7", trail_name = "Cedar Loop" },
    { trail_id = "8", trail_name = "Eagle Ridge" },
    { trail_id = "9", trail_name = "Bear Claw Path" }
  ]
}


# INSERT TEST DATA INTO TrailDeviceLogs
resource "aws_dynamodb_table_item" "trail_device_logs_items" {
  for_each = { for idx, item in var.trail_device_logs_sampledata : idx => item }

  table_name = aws_dynamodb_table.trail_device_logs.name
  hash_key   = aws_dynamodb_table.trail_device_logs.hash_key
  range_key  = aws_dynamodb_table.trail_device_logs.range_key

  item = jsonencode({
    trail_id         = { "N" = each.value.trail_id }
    device_timestamp = { "S" = each.value.device_timestamp }
    device_id        = { "S" = each.value.device_id }
    timestamp        = { "N" = each.value.timestamp }
    battery          = { "N" = each.value.battery }
  })
}

# INSERT TEST DATA INTO DeviceMetadata
resource "aws_dynamodb_table_item" "device_metadata_items" {
  for_each = { for idx, item in var.device_metadata_sampledata : idx => item }

  table_name = aws_dynamodb_table.device_metadata.name
  hash_key   = aws_dynamodb_table.device_metadata.hash_key

  item = jsonencode({
    device_id        = { "S" = each.value.device_id }
    current_trail_id = { "N" = each.value.current_trail_id }
    battery          = { "N" = each.value.battery }
    last_update      = { "N" = each.value.last_update }
  })
}

# INSERT TEST DATA INTO TrailMetadata
resource "aws_dynamodb_table_item" "trail_metadata_items" {
  for_each = { for idx, item in var.trail_metadata_sampledata : idx => item }

  table_name = aws_dynamodb_table.trail_metadata.name
  hash_key   = aws_dynamodb_table.trail_metadata.hash_key

  item = jsonencode({
    trail_id   = { "N" = each.value.trail_id }
    trail_name = { "S" = each.value.trail_name }
  })
}