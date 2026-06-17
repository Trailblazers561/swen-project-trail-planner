# TABLE 1: Device
resource "aws_dynamodb_table" "device_table" {
  name           = "${var.deploy_env}_trailcount_device_table"
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
    date_manufactured: number (UNIX timestamp)
    date_retired: number (UNIX timestamp)
    is_blocked: boolean
    is_archived: boolean
  */
}

# TABLE 2: Trail
resource "aws_dynamodb_table" "trail_table" {
  name           = "${var.deploy_env}_trailcount_trail_table"
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
  name           = "${var.deploy_env}_trailcount_device_trail_table"
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

# TABLE 4: Area
resource "aws_dynamodb_table" "area_table" {
  name           = "${var.deploy_env}_trailcount_area_table"
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
  name           = "${var.deploy_env}_trailcount_device_trail_log_hour_table"
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
  name           = "${var.deploy_env}_trailcount_device_trail_log_day_table"
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

# TABLE 7: DeviceTrailLogWeek
resource "aws_dynamodb_table" "device_trail_log_week_table" {
  name           = "${var.deploy_env}_trailcount_device_trail_log_week_table"
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

# TABLE 8: DeviceTrailLogMonth
resource "aws_dynamodb_table" "device_trail_log_month_table" {
  name           = "${var.deploy_env}_trailcount_device_trail_log_month_table"
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

# TABLE 9: DeviceLog
resource "aws_dynamodb_table" "device_log_table" {
  name           = "${var.deploy_env}_trailcount_device_log_table"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "device_id"
  range_key    = "time"

  attribute {
    name = "device_id"
    type = "N" // FK
  }

  attribute {
    name = "time"
    type = "N" // number (UNIX timestamp)
  }

  /*
    count: number (int)
    battery: number (percentage)
    firmware_version: string
    rssi: number (int, dBm)
    rsrp: number (int, dBm)
    rsrq: number (int, dB)
  */
}

# TABLE 10: Errors
resource "aws_dynamodb_table" "error_table" {
  name           = "${var.deploy_env}_trailcount_error_table"
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

# TABLE 11: Registration
resource "aws_dynamodb_table" "registration_table" {
  name         = "${var.deploy_env}_trailcount_registration_table"
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

locals {
  device_sample_data = csvdecode(file("${path.module}/${local.sample_data_directory}/devices.csv"))
  trail_sample_data = csvdecode(file("${path.module}/${local.sample_data_directory}/trails.csv"))
  device_trail_sample_data = csvdecode(file("${path.module}/${local.sample_data_directory}/device_trails.csv"))
  areas_raw = csvdecode(file("${path.module}/${local.sample_data_directory}/areas.csv"))
  area_sample_data = [
    for area_name in distinct([for a in local.areas_raw : a.name]) : {
      name = area_name
      trail_ids = [
        for a in local.areas_raw :
        a.trail_id
        if a.name == area_name
      ]
    }
  ]
  device_log_sample_data = csvdecode(file("${path.module}/${local.sample_data_directory}/device_logs.csv"))
  error_sample_data = csvdecode(file("${path.module}/${local.sample_data_directory}/errors.csv"))
  registration_sample_data = csvdecode(file("${path.module}/${local.sample_data_directory}/registrations.csv"))
}

# INSERT TEST DATA INTO Device
resource "aws_dynamodb_table_item" "device_items" {
  for_each = { for idx, item in local.device_sample_data : idx => item }

  table_name = aws_dynamodb_table.device_table.name
  hash_key = aws_dynamodb_table.device_table.hash_key

  item = jsonencode({
    id = { "N" = each.value.id }
    name = { "S" = each.value.name }
    notes = { "S" = each.value.notes }
    date_manufactured = { "N" = each.value.date_manufactured }
  })
}

# INSERT TEST DATA INTO Trail
resource "aws_dynamodb_table_item" "trail_items" {
  for_each = { for idx, item in local.trail_sample_data : idx => item }

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
  for_each = { for idx, item in local.device_trail_sample_data : idx => item }

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

# INSERT TEST DATA INTO Areas
resource "aws_dynamodb_table_item" "area_items" {
  for_each = { for idx, item in local.area_sample_data : idx => item }

  table_name = aws_dynamodb_table.area_table.name
  hash_key   = aws_dynamodb_table.area_table.hash_key

  item = jsonencode({
    name = { "S" = each.value.name }
    trail_ids  = { "L" = [for id in each.value.trail_ids : { "N" = id }] }
  })
}

# INSERT TEST DATA INTO DeviceLog
resource "aws_dynamodb_table_item" "device_log_items" {
  for_each = { for idx, item in local.device_log_sample_data : idx => item }

  table_name = aws_dynamodb_table.device_log_table.name
  hash_key   = aws_dynamodb_table.device_log_table.hash_key
  range_key  = aws_dynamodb_table.device_log_table.range_key

  item = jsonencode({
    device_id  = { "N" = each.value.device_id }
    time = { "N" = each.value.time }
    count = { "N" = each.value.count }
    battery = { "N" = each.value.battery }
    firmware_version = { "S" = each.value.firmware_version }
    rssi = { "N" = each.value.rssi }
    rsrp = { "N" = each.value.rsrp }
    rsrq = { "N" = each.value.rsrq }
  })
}

# INSERT TEST DATA INTO Error
resource "aws_dynamodb_table_item" "error_items" {
  for_each = { for idx, item in local.error_sample_data : idx => item }

  table_name = aws_dynamodb_table.error_table.name
  hash_key   = aws_dynamodb_table.error_table.hash_key
  range_key  = aws_dynamodb_table.error_table.range_key

  item = jsonencode({
    id  = { "N" = each.value.id }
    time = { "N" = each.value.time }
    error = { "S" = each.value.error }
  })
}

# INSERT TEST DATA INTO Registration
resource "aws_dynamodb_table_item" "registration_items" {
  for_each = { for idx, item in local.registration_sample_data : idx => item }

  table_name = aws_dynamodb_table.registration_table.name
  hash_key   = aws_dynamodb_table.registration_table.hash_key
  range_key  = aws_dynamodb_table.registration_table.range_key

  item = jsonencode({
    registration_id  = { "N" = each.value.registration_id }
    device_id  = { "N" = each.value.device_id }
    date_registered = { "N" = each.value.date_registered }
    cert_time_to_live = { "N" = each.value.cert_time_to_live }
  })
}