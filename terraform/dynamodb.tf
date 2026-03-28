# TABLE 1: Device
resource "aws_dynamodb_table" "device_table" {
  name           = "${var.deploy_env}_Device"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "id"

  attribute {
    name = "id"
    type = "N" // int (PK)
  }

  /*
    name: string
    notes: string
    firmware_version: string
    date_manufactured: number (UNIX timestamp)
    date_retired: number (UNIX timestamp)
  */
}

# TABLE 2: Trail
resource "aws_dynamodb_table" "trail_table" {
  name           = "${var.deploy_env}_Trail"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "id"

  attribute {
    name = "id"
    type = "N" // int (PK)
  }

  /*
    notes: string
    name: string
    latitude: number (UNIX timestamp)
    longitude: number (UNIX timestamp)
  */
}

# TABLE 3: DeviceTrail
resource "aws_dynamodb_table" "device_trail_table" {
  name           = "${var.deploy_env}_DeviceTrail"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "device_id"

  attribute {
    name = "device_id"
    type = "N" // int (FK)
  }

  attribute {
    name = "trail_id"
    type = "N" // int (FK)
  }

  global_secondary_index {
    name            = "trail-index"
    hash_key        = "trail_id"
    projection_type = "ALL"
  }

  /*
    id: number
    notes: string
    date_installed: number (UNIX timestamp)
    date_removed: number (UNIX timestamp)
  */
}

# TABLE 4: TrailGroup
resource "aws_dynamodb_table" "trail_group_table" {
  name           = "${var.deploy_env}_TrailGroup"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "name"

  attribute {
    name = "name"
    type = "S" // PK
  }

  /*
    trails: number list (trail_id)
  */
}

# TABLE 5: DeviceTrailLogHour
resource "aws_dynamodb_table" "device_trail_log_hour_table" {
  name           = "${var.deploy_env}_DeviceTraiLogHour"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "device_trail_id"
  range_key    = "start"

  attribute {
    name = "device_trail_id"
    type = "N" // FK
  }

  attribute {
    name = "start"
    type = "N" // number (UNIX timestamp)
  }

  /*
    count: number (int)
  */
}

# TABLE 6: DeviceTrailLogDay
resource "aws_dynamodb_table" "device_trail_log_day_table" {
  name           = "${var.deploy_env}_DeviceTraiLogDays"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "device_trail_id"
  range_key    = "start"

  attribute {
    name = "device_trail_id"
    type = "N" // FK
  }

  attribute {
    name = "start"
    type = "N" // number (UNIX timestamp)
  }

  /*
    count: number (int)
    battery: number (percentage)
  */
}

# TABLE 7: DeviceTrailLogWeek
resource "aws_dynamodb_table" "device_trail_log_week_table" {
  name           = "${var.deploy_env}_DeviceTrailLogWeeks"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "device_trail_id"
  range_key    = "start"

  attribute {
    name = "device_trail_id"
    type = "N" // FK
  }

  attribute {
    name = "start"
    type = "N" // number (UNIX timestamp)
  }

  /*
    count: number (int)
    battery: number (percentage)
  */
}

# TABLE 8: DeviceTrailLogMonth
resource "aws_dynamodb_table" "device_trail_log_month_table" {
  name           = "${var.deploy_env}_DeviceTraiLogMonths"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "device_trail_id"
  range_key    = "start"

  attribute {
    name = "device_trail_id"
    type = "N" // FK
  }

  attribute {
    name = "start"
    type = "N" // number (UNIX timestamp)
  }

  /*
    count: number (int)
    battery: number (percentage)
  */
}

# TABLE 9: Errors
resource "aws_dynamodb_table" "error_table" {
  name           = "${var.deploy_env}_Error"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "id"
  range_key = "time"

  attribute {
    name = "id"
    type = "N" // FK
  }

  attribute {
    name = "time"
    type = "N" // number (UNIX timestamp)
  }

  /*
    error: string
  */
}


# # VARIABLES: SAMPLE DATA
# variable "trail_device_logs_sampledata" {
#   type = list(object({
#     trail_id  = string
#     device_id = string
#     timestamp = string
#     battery   = string
#   }))
#   # Sample data will get created 
#   default = [
#   ]
# }

# variable "device_metadata_sampledata" {
#   type = list(object({
#     device_id         = string
#     current_trail_id  = string
#     battery           = string
#     last_update       = string
#   }))
#   default = [
#     {
#       device_id        = "1"
#       current_trail_id = "1"
#       battery          = "98"
#       last_update      = "1771863877"
#     },
#     {
#       device_id        = "2"
#       current_trail_id = "2"
#       battery          = "89"
#       last_update      = "1771863877"
#     },
#     {
#       device_id        = "3"
#       current_trail_id = "3"
#       battery          = "100"
#       last_update      = "1771863877"
#     },
#     {
#       device_id        = "4"
#       current_trail_id = "4"
#       battery          = "85"
#       last_update      = "1771863877"
#     },
#     {
#       device_id        = "5"
#       current_trail_id = "5"
#       battery          = "60"
#       last_update      = "1771863877"
#     },
#     {
#       device_id        = "6"
#       current_trail_id = "6"
#       battery          = "70"
#       last_update      = "1771863877"
#     },
#     {
#       device_id        = "7"
#       current_trail_id = "7"
#       battery          = "99"
#       last_update      = "1771863877"
#     },
#     {
#       device_id        = "8"
#       current_trail_id = "8"
#       battery          = "94"
#       last_update      = "1771863877"
#     },
#     {
#       device_id        = "9"
#       current_trail_id = "9"
#       battery          = "51"
#       last_update      = "1771863877"
#     },
#     {
#       device_id        = "10"
#       current_trail_id = "10"
#       battery          = "62"
#       last_update      = "1771863877"
#     }
#   ]
# }

# variable "trail_metadata_sampledata" {
#   type = list(object({
#     trail_id   = string
#     trail_name = string
#   }))
#   default = [
#     { trail_id = "1", trail_name = "Mt. Marcy" },
#     { trail_id = "2", trail_name = "Giant Mountain" },
#     { trail_id = "3", trail_name = "Poke-O-Moonshine Ranger Trail" },
#     { trail_id = "4", trail_name = "Mt. Skylight" },
#     { trail_id = "5", trail_name = "Cat Mountain" },
#     { trail_id = "6", trail_name = "Bald Peak" },
#     { trail_id = "7", trail_name = "Mt. Haystack" },
#     { trail_id = "8", trail_name = "Beaver Meadow Trail" },
#     { trail_id = "9", trail_name = "Mud Lake" },
#     { trail_id = "10", trail_name = "Blueberry Trail"}
#   ]
# }

# variable "trail_groups_sampledata" {
#   type = list(object({
#     group_name = string
#     trail_ids  = list(string)
#   }))

#   default = [
#     {
#       group_name = "High Peaks Wilderness"
#       trail_ids  = ["1", "4", "7", "10"] # Mt. Marcy, Mt. Skylight, Mt. Haystack, Blueberry Trail
#     },
#     {
#       group_name = "Giant Mountain Wilderness"
#       trail_ids  = ["2", "6"] # Giant Mountain, Bald Peak
#     },
#     {
#       group_name = "Adirondack Park"
#       trail_ids = [ "5", "9" ] # Cat Mountain, Mud Lake
#     }
#   ]
# }


# # INSERT TEST DATA INTO TrailDeviceLogs
# resource "aws_dynamodb_table_item" "trail_device_logs_items" {
#   for_each = { for idx, item in var.trail_device_logs_sampledata : idx => item }

#   table_name = aws_dynamodb_table.trail_device_logs.name
#   hash_key   = aws_dynamodb_table.trail_device_logs.hash_key
#   range_key  = aws_dynamodb_table.trail_device_logs.range_key

#   item = jsonencode({
#     trail_id  = { "N" = each.value.trail_id }
#     timestamp = { "N" = each.value.timestamp }
#     device_id = { "S" = each.value.device_id }
#     battery   = { "N" = each.value.battery }
#   })
# }

# # INSERT TEST DATA INTO DeviceMetadata
# resource "aws_dynamodb_table_item" "device_metadata_items" {
#   for_each = { for idx, item in var.device_metadata_sampledata : idx => item }

#   table_name = aws_dynamodb_table.device_metadata.name
#   hash_key   = aws_dynamodb_table.device_metadata.hash_key

#   item = jsonencode({
#     device_id        = { "S" = each.value.device_id }
#     current_trail_id = { "N" = each.value.current_trail_id }
#     battery          = { "N" = each.value.battery }
#     last_update      = { "N" = each.value.last_update }
#   })
# }

# # INSERT TEST DATA INTO TrailMetadata
# resource "aws_dynamodb_table_item" "trail_metadata_items" {
#   for_each = { for idx, item in var.trail_metadata_sampledata : idx => item }

#   table_name = aws_dynamodb_table.trail_metadata.name
#   hash_key   = aws_dynamodb_table.trail_metadata.hash_key

#   item = jsonencode({
#     trail_id   = { "N" = each.value.trail_id }
#     trail_name = { "S" = each.value.trail_name }
#   })
# }

# # INSERT TEST DATA INTO TrailGroups
# resource "aws_dynamodb_table_item" "trail_groups_items" {
#   for_each = { for idx, item in var.trail_groups_sampledata : idx => item }

#   table_name = aws_dynamodb_table.trail_groups.name
#   hash_key   = aws_dynamodb_table.trail_groups.hash_key

#   item = jsonencode({
#     group_name = { "S" = each.value.group_name }
#     trail_ids  = { "L" = [for id in each.value.trail_ids : { "N" = id }] }
#   })
# }