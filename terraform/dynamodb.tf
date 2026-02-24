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
  name           = "${var.deploy_env}_DeviceMetadata"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "device_id"

  attribute {
    name = "device_id"
    type = "N"
  }

  tags = {
    Environment = "dev"
    TableType   = "Metadata"
  }
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
}

# VARIABLES: SAMPLE DATA
variable "trail_device_logs_sampledata" {
  type = list(object({
    trail_id  = string
    device_id = string
    timestamp = string
    battery   = string
  }))
  # Sample data will get created 
  default = [
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
      device_id        = "1"
      current_trail_id = "1"
      battery          = "98"
      last_update      = "1771863877"
    },
    {
      device_id        = "2"
      current_trail_id = "2"
      battery          = "89"
      last_update      = "1771863877"
    },
    {
      device_id        = "3"
      current_trail_id = "3"
      battery          = "100"
      last_update      = "1771863877"
    },
    {
      device_id        = "4"
      current_trail_id = "4"
      battery          = "85"
      last_update      = "1771863877"
    },
    {
      device_id        = "5"
      current_trail_id = "5"
      battery          = "60"
      last_update      = "1771863877"
    },
    {
      device_id        = "6"
      current_trail_id = "6"
      battery          = "70"
      last_update      = "1771863877"
    },
    {
      device_id        = "7"
      current_trail_id = "7"
      battery          = "99"
      last_update      = "1771863877"
    },
    {
      device_id        = "8"
      current_trail_id = "8"
      battery          = "94"
      last_update      = "1771863877"
    },
    {
      device_id        = "9"
      current_trail_id = "9"
      battery          = "51"
      last_update      = "1771863877"
    },
    {
      device_id        = "10"
      current_trail_id = "10"
      battery          = "62"
      last_update      = "1771863877"
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
    { trail_id = "2", trail_name = "Giant Mountain" },
    { trail_id = "3", trail_name = "Poke-O-Moonshine Ranger Trail" },
    { trail_id = "4", trail_name = "Mt. Skylight" },
    { trail_id = "5", trail_name = "Cat Mountain" },
    { trail_id = "6", trail_name = "Bald Peak" },
    { trail_id = "7", trail_name = "Mt. Haystack" },
    { trail_id = "8", trail_name = "Beaver Meadow Trail" },
    { trail_id = "9", trail_name = "Mud Lake" },
    { trail_id = "10", trail_name = "Blueberry Trail"}
  ]
}

variable "trail_groups_sampledata" {
  type = list(object({
    group_name = string
    trail_ids  = list(string)
  }))

  default = [
    {
      group_name = "High Peaks Wilderness"
      trail_ids  = ["1", "4", "7", "10"] # Mt. Marcy, Mt. Skylight, Mt. Haystack, Blueberry Trail
    },
    {
      group_name = "Giant Mountain Wilderness"
      trail_ids  = ["2", "6"] # Giant Mountain, Bald Peak
    },
    {
      group_name = "Adirondack Park"
      trail_ids = [ "5", "9" ] # Cat Mountain, Mud Lake
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
    device_id = { "N" = each.value.device_id }
    battery   = { "N" = each.value.battery }
  })

  lifecycle {
    ignore_changes = [item]
  }
}

# INSERT TEST DATA INTO DeviceMetadata
resource "aws_dynamodb_table_item" "device_metadata_items" {
  for_each = { for idx, item in var.device_metadata_sampledata : idx => item }

  table_name = aws_dynamodb_table.device_metadata.name
  hash_key   = aws_dynamodb_table.device_metadata.hash_key

  item = jsonencode({
    device_id        = { "N" = each.value.device_id }
    current_trail_id = { "N" = each.value.current_trail_id }
    battery          = { "N" = each.value.battery }
    last_update      = { "N" = each.value.last_update }
  })

  lifecycle {
    ignore_changes = [item]
  }
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

  lifecycle {
    ignore_changes = [item]
  }
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

  lifecycle {
    ignore_changes = [item]
  }
}