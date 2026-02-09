# TABLE 1: TrailDeviceLogs
resource "aws_dynamodb_table" "trail_device_logs" {
  name         = "${var.deploy_env}_TrailDeviceLogs"
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

#   lifecycle {
#    prevent_destroy = true
#  }
}

# TABLE 2: DeviceMetadata
resource "aws_dynamodb_table" "device_metadata" {
  name           = "${var.deploy_env}_DeviceMetadata"
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

#   lifecycle {
#    prevent_destroy = true
#  }
}

# TABLE 3: TrailMetadata
resource "aws_dynamodb_table" "trail_metadata" {
  name           = "${var.deploy_env}_TrailMetadata"
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

#   lifecycle {
#    prevent_destroy = true
#  }
}

# TABLE 4: TrailGroups
resource "aws_dynamodb_table" "trail_groups" {
  name           = "${var.deploy_env}_TrailGroups"
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

#   lifecycle {
#    prevent_destroy = true
#  }
}

# VARIABLES: SAMPLE DATA
variable "trail_device_logs_sampledata" {
  type = list(object({
    trail_id  = string
    device_id = string
    timestamp = string
    battery   = string
  }))
  default = [
    {
      trail_id  = "1"
      device_id = "deviceA"
      timestamp = "1759064864"
      battery   = "95"
    },
    {
      trail_id  = "1"
      device_id = "deviceA"
      timestamp = "1759065044"
      battery   = "94"
    },
    {
      trail_id  = "2"
      device_id = "deviceB"
      timestamp = "1759065344"
      battery   = "88"
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
      last_update      = "1759065044"
    },
    {
      device_id        = "deviceB"
      current_trail_id = "2"
      battery          = "88"
      last_update      = "1759065344"
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

variable "trail_groups_sampledata" {
  type = list(object({
    group_name = string
    trail_ids  = list(string)
  }))

  default = [
    {
      group_name = "All Areas"
      trail_ids  = ["1","2","3","4","5","6","7","8","9"] # all trails by ID
    },
    {
      group_name = "Five Ponds"
      trail_ids  = ["5","6","7"] # Blueberry Trail, Sunset Peak, Cedar Loop
    },
    {
      group_name = "High Peaks"
      trail_ids  = ["1","2"] # Mt. Marcy, Wolf Creek Mountain
    },
    {
      group_name = "Giant Mountain"
      trail_ids  = ["3","4"] # Mt. Joe, Mt. America
    }
  ]
}


# INSERT TEST DATA INTO TrailDeviceLogs
resource "aws_dynamodb_table_item" "trail_device_logs_items" {
  for_each = { for idx, item in var.trail_device_logs_sampledata : idx => item }

  table_name = aws_dynamodb_table.trail_device_logs.name
  hash_key   = aws_dynamodb_table.trail_device_logs.hash_key
  range_key  = aws_dynamodb_table.trail_device_logs.range_key

  item = jsonencode({
    trail_id  = { "N" = each.value.trail_id }
    timestamp = { "N" = each.value.timestamp }
    device_id = { "S" = each.value.device_id }
    battery   = { "N" = each.value.battery }
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

# INSERT TEST DATA INTO TrailGroups
resource "aws_dynamodb_table_item" "trail_groups_items" {
  for_each = { for idx, item in var.trail_groups_sampledata : idx => item }

  table_name = aws_dynamodb_table.trail_groups.name
  hash_key   = aws_dynamodb_table.trail_groups.hash_key

  item = jsonencode({
    group_name = { "S" = each.value.group_name }
    trail_ids  = { "L" = [for id in each.value.trail_ids : { "N" = id }] }
  })
}