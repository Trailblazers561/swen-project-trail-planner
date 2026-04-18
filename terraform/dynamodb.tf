# TABLE 1: Device
resource "aws_dynamodb_table" "device_table" {
  name           = "${var.deploy_env}_Device"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "id"

  attribute {
    name = "id"
    type = "N" // int (PK)
  }

  attribute {
    name = "name"
    type = "S"
  }

  global_secondary_index {
    name            = "name-index"
    hash_key        = "name"
    projection_type = "ALL"
  }

  /*
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
    latitude: number (float)
    longitude: number (float)
    date_activated: number (UNIX timestamp)
    date_retired: number (UNIX timestamp)
  */
}

# TABLE 3: DeviceTrail
resource "aws_dynamodb_table" "device_trail_table" {
  name           = "${var.deploy_env}_DeviceTrail"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "device_id"
  range_key = "date_installed"

  attribute {
    name = "device_id"
    type = "N" // int (FK)
  }

  attribute {
    name = "trail_id"
    type = "N" // int (FK)
  }

  attribute {
    name = "date_installed"
    type = "N" // number (UNIX timestamp)
  }


  global_secondary_index {
    name            = "trail-index"
    hash_key        = "trail_id"
    range_key = "date_installed"
    projection_type = "ALL"
  }

  /*
    id: number (int)
    notes: string
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
  name           = "${var.deploy_env}_DeviceTrailLogHour"
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
  name           = "${var.deploy_env}_DeviceTrailLogDay"
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
  name           = "${var.deploy_env}_DeviceTrailLogWeek"
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
  name           = "${var.deploy_env}_DeviceTrailLogMonth"
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

# TABLE 10: Registration
resource "aws_dynamodb_table" "registration_table" {
  name         = "${var.deploy_env}_Registration"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "registration_id"

  attribute {
    name = "registration_id"
    type = "N"
  }

    attribute {
    name = "device_id"
    type = "N"
  }

    global_secondary_index {
    name            = "device-index"
    hash_key        = "device_id"
    projection_type = "ALL"
  }

  /*
    date_registered: number (UNIX timestamp)
    cert_time_to_live: number (int, seconds)
  */
}

# VARIABLES: SAMPLE DATA
variable "device_sampledata" {
  type = list(object({
    id = string
    name = string
    notes = string
    firmware_version = string
    date_manufactured = string
  }))

  default = [
    {
      id = "1"
      name = "f1c9645dbc14efddc7d8a322685f26eb3c0b65c6d5aeb89f9a3a98a4f8f5c0d3"
      notes = "this is a pretty neat device right"
      firmware_version = "1.0.0"
      date_manufactured = "1767225600"
    },
    {
      id = "2"
      name = "6ae48c0dcbd66a4d287f9cf05d2f2d2ff93a39b3dcd7db4a4f16279806b4f083"
      notes = "this is a pretty neat device right"
      firmware_version = "1.0.0"
      date_manufactured = "1767225600"
    },
    {
      id = "3"
      name = "20f244d703c66e79ebfa8c7c978bcf2a9e92c1d4f894f5e2eb39e5c9b32c9f44"
      notes = "this is a pretty neat device right"
      firmware_version = "1.0.0"
      date_manufactured = "1767225600"
    },
    {
      id = "4"
      name = "3e6e3bb1da8d5903b59b308fc7db71e1d2da4d1e9dfe239e95ed6f9f851a5b57"
      notes = "this is a pretty neat device right"
      firmware_version = "1.0.0"
      date_manufactured = "1767225600"
    },
    {
      id = "5"
      name = "521d2b7e4208a8c6480c78ec4c92f4877fa9f2b16f57d9df514f8c84e218c3d1"
      notes = "this is a pretty neat device right"
      firmware_version = "1.0.0"
      date_manufactured = "1767225600"
    },
    {
      id = "6"
      name = "a0fa9d6459f4b6e446c7d5c9e38e4e6d9ffb21c5dcf2f3f18a9230ed86d6fa32"
      notes = "this is a pretty neat device right"
      firmware_version = "1.0.0"
      date_manufactured = "1767225600"
    },
    {
      id = "7"
      name = "9e62b2b0c7f4f94e3b95f65e324d64c34e94f3e20a7b5f492c4b0d8f9a7c6f2d"
      notes = "this is a pretty neat device right"
      firmware_version = "1.0.0"
      date_manufactured = "1767225600"
    },
    {
      id = "8"
      name = "bcf4d9f0c3a54e1c8b2f9d7f4e8a2c9b7d1f6e3a9c8d0e5b1f3a6c7d2e8f9b0a"
      notes = "this is a pretty neat device right"
      firmware_version = "1.0.0"
      date_manufactured = "1767225600"
    },
    {
      id = "9"
      name = "7d3b2f1c4e5a6d7b8c9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c"
      notes = "this is a pretty neat device right"
      firmware_version = "1.0.0"
      date_manufactured = "1767225600"
    },
    {
      id = "10"
      name = "c2b3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3"
      notes = "this is a pretty neat device right"
      firmware_version = "1.0.0"
      date_manufactured = "1767225600"
    },
  ]
}

variable "trail_sampledata" {
  type = list(object({
    id   = string
    name = string
    latitude = string
    longitude = string
    notes = string
    date_activated = string
  }))

  default = [
    {
      id = "1"
      name = "Mt. Marcy"
      latitude = "44.1829"
      longitude = "-73.96349"
      notes = "The highest peak in New York"
      date_activated = "1767225600"
    },
    {
      id = "2"
      name = "Giant Mountain"
      latitude = "44.13838"
      longitude = "-73.74374"
      notes = "It's Giant"
      date_activated = "1767225600"
    },
    {
      id = "3"
      name = "Poke-O-Moonshine Ranger Trail"
      latitude = "44.4036"
      longitude = "-73.50241"
      notes = "Has some great rock climbing routes"
      date_activated = "1767225600"
    },
    {
      id = "4"
      name = "Mt. Skylight"
      latitude = "44.18123"
      longitude = "-73.96592"
      notes = "It is widely considered nature's skylight"
      date_activated = "1767225600"
    },
    {
      id = "5"
      name = "Cat Mountain"
      latitude = "43.57609"
      longitude = "-73.68584"
      notes = "There could be cats!"
      date_activated = "1767225600"
    },
    {
      id = "6"
      name = "Bald Peak"
      latitude = "44.14989"
      longitude = "-73.62672"
      notes = "It's really bald!"
      date_activated = "1767225600"
    },
    {
      id = "7"
      name = "Mt. Haystack"
      latitude = "44.18896"
      longitude = "-73.81613"
      notes = "Filled with many steep, challenging obstacles"
      date_activated = "1767225600"
    },
    {
      id = "8"
      name = "Beaver Meadow Trail"
      latitude = "44.14958"
      longitude = "-73.76836"
      notes = "Don't anger the beavers living here!"
      date_activated = "1767225600"
    },
    {
      id = "9"
      name = "Mud Lake"
      latitude = "43.21285"
      longitude = "-74.20863"
      notes = "Be sure to bring boots!"
      date_activated = "1767225600"
    },
    {
      id = "10"
      name = "Blueberry Trail"
      latitude = "44.19171"
      longitude = "-74.2635"
      notes = "A relaxing trail lined with the greatest blue fruit, blueberries!"
      date_activated = "1767225600"
    }
  ]
}

variable "device_trail_sampledata" {
  type = list(object({
    id = string
    device_id = string
    trail_id = string
    notes = string
    date_installed = string
  }))

  default = [
    {
      id = "1"
      device_id = "1"
      trail_id = "1"
      notes = "device trail association notes"
      date_installed = "1767225600"
    },
    {
      id = "2"
      device_id = "2"
      trail_id = "2"
      notes = "device trail association notes"
      date_installed = "1767225600"
    },
    {
      id = "3"
      device_id = "3"
      trail_id = "3"
      notes = "device trail association notes"
      date_installed = "1767225600"
    },
    {
      id = "4"
      device_id = "4"
      trail_id = "4"
      notes = "device trail association notes"
      date_installed = "1767225600"
    },
    {
      id = "5"
      device_id = "5"
      trail_id = "5"
      notes = "device trail association notes"
      date_installed = "1767225600"
    },
    {
      id = "6"
      device_id = "6"
      trail_id = "6"
      notes = "device trail association notes"
      date_installed = "1767225600"
    },
    {
      id = "7"
      device_id = "7"
      trail_id = "7"
      notes = "device trail association notes"
      date_installed = "1767225600"
    },
    {
      id = "8"
      device_id = "8"
      trail_id = "8"
      notes = "device trail association notes"
      date_installed = "1767225600"
    },
    {
      id = "9"
      device_id = "9"
      trail_id = "9"
      notes = "device trail association notes"
      date_installed = "1767225600"
    },
    {
      id = "10"
      device_id = "10"
      trail_id = "10"
      notes = "device trail association notes"
      date_installed = "1767225600"
    },
  ]
}

variable "trail_groups_sampledata" {
  type = list(object({
    name = string
    trail_ids  = list(string)
  }))

  default = [
    {
      name = "High Peaks Wilderness"
      trail_ids  = ["1", "4", "7", "10"] # Mt. Marcy, Mt. Skylight, Mt. Haystack, Blueberry Trail
    },
    {
      name = "Giant Mountain Wilderness"
      trail_ids  = ["2", "6"] # Giant Mountain, Bald Peak
    },
    {
      name = "Adirondack Park"
      trail_ids = ["5", "9"] # Cat Mountain, Mud Lake
    }
  ]
}

variable "device_trail_log_hour_sampledata" {
  type = list(object({
    device_trail_id  = string
    start = string
    count = string
  }))

  # Empty for now
  default = [
  ]
}

variable "device_trail_log_day_sampledata" {
  type = list(object({
    device_trail_id  = string
    start = string
    count = string
    battery   = string
  }))

  # Empty for now
  default = [
  ]
}

variable "device_trail_log_week_sampledata" {
  type = list(object({
    device_trail_id  = string
    start = string
    count = string
    battery   = string
  }))

  # Empty for now
  default = [
  ]
}

variable "device_trail_log_month_sampledata" {
  type = list(object({
    device_trail_id  = string
    start = string
    count = string
    battery   = string
  }))

  # Empty for now
  default = [
  ]
}

# INSERT TEST DATA INTO Device
resource "aws_dynamodb_table_item" "device_items" {
  for_each = { for idx, item in var.device_sampledata : idx => item }

  table_name = aws_dynamodb_table.device_table.name
  hash_key = aws_dynamodb_table.device_table.hash_key

  item = jsonencode({
    id = { "N" = each.value.id }
    name = { "S" = each.value.name }
    notes = { "S" = each.value.notes }
    firmware_version = { "S" = each.value.firmware_version }
    date_manufactured = { "N" = each.value.date_manufactured }
  })
}

# INSERT TEST DATA INTO Trail
resource "aws_dynamodb_table_item" "trail_items" {
  for_each = { for idx, item in var.trail_sampledata : idx => item }

  table_name = aws_dynamodb_table.trail_table.name
  hash_key = aws_dynamodb_table.trail_table.hash_key

  item = jsonencode({
    id = { "N" = each.value.id }
    name = { "S" = each.value.name }
    latitude = { "N" = each.value.latitude }
    longitude = { "N" = each.value.longitude }
    notes = { "S" = each.value.notes }
    date_activated = { "N" = each.value.date_activated }
  })
}

# INSERT TEST DATA INTO DeviceTrail
resource "aws_dynamodb_table_item" "device_trail_items" {
  for_each = { for idx, item in var.device_trail_sampledata : idx => item }

  table_name = aws_dynamodb_table.device_trail_table.name
  hash_key = aws_dynamodb_table.device_trail_table.hash_key
  range_key = aws_dynamodb_table.device_trail_table.range_key

  item = jsonencode({
    id = { "N" = each.value.id }
    device_id = { "N" = each.value.device_id }
    trail_id = { "N" = each.value.trail_id }
    notes = { "S" = each.value.notes }
    date_installed = { "N" = each.value.date_installed }
  })
}

# INSERT TEST DATA INTO TrailGroups
resource "aws_dynamodb_table_item" "trail_group_items" {
  for_each = { for idx, item in var.trail_groups_sampledata : idx => item }

  table_name = aws_dynamodb_table.trail_group_table.name
  hash_key   = aws_dynamodb_table.trail_group_table.hash_key

  item = jsonencode({
    name = { "S" = each.value.name }
    trail_ids  = { "L" = [for id in each.value.trail_ids : { "N" = id }] }
  })
}

# INSERT TEST DATA INTO DeviceTrailLogHour
resource "aws_dynamodb_table_item" "device_trail_log_hour_items" {
  for_each = { for idx, item in var.device_trail_log_hour_sampledata : idx => item }

  table_name = aws_dynamodb_table.device_trail_log_hour_table.name
  hash_key   = aws_dynamodb_table.device_trail_log_hour_table.hash_key
  range_key  = aws_dynamodb_table.device_trail_log_hour_table.range_key

  item = jsonencode({
    device_trail_id  = { "N" = each.value.device_trail_id }
    start = { "N" = each.value.start }
    count = { "N" = each.value.count }
  })
}

# INSERT TEST DATA INTO DeviceTrailLogDay
resource "aws_dynamodb_table_item" "device_trail_log_day_items" {
  for_each = { for idx, item in var.device_trail_log_hour_sampledata : idx => item }

  table_name = aws_dynamodb_table.device_trail_log_day_table.name
  hash_key   = aws_dynamodb_table.device_trail_log_day_table.hash_key
  range_key  = aws_dynamodb_table.device_trail_log_day_table.range_key

  item = jsonencode({
    device_trail_id  = { "N" = each.value.device_trail_id }
    start = { "N" = each.value.start }
    count = { "N" = each.value.count }
    battery = { "N" = each.value.battery }
  })
}

# INSERT TEST DATA INTO DeviceTrailLogWeek
resource "aws_dynamodb_table_item" "device_trail_log_week_items" {
  for_each = { for idx, item in var.device_trail_log_week_sampledata : idx => item }

  table_name = aws_dynamodb_table.device_trail_log_week_table.name
  hash_key   = aws_dynamodb_table.device_trail_log_week_table.hash_key
  range_key  = aws_dynamodb_table.device_trail_log_week_table.range_key

  item = jsonencode({
    device_trail_id  = { "N" = each.value.device_trail_id }
    start = { "N" = each.value.start }
    count = { "N" = each.value.count }
    battery = { "N" = each.value.battery }
  })
}

# INSERT TEST DATA INTO DeviceTrailLogMonth
resource "aws_dynamodb_table_item" "device_trail_log_month_items" {
  for_each = { for idx, item in var.device_trail_log_month_sampledata : idx => item }

  table_name = aws_dynamodb_table.device_trail_log_month_table.name
  hash_key   = aws_dynamodb_table.device_trail_log_month_table.hash_key
  range_key  = aws_dynamodb_table.device_trail_log_month_table.range_key

  item = jsonencode({
    device_trail_id  = { "N" = each.value.device_trail_id }
    start = { "N" = each.value.start }
    count = { "N" = each.value.count }
    battery = { "N" = each.value.battery }
  })
}