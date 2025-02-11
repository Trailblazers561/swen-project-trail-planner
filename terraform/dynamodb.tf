resource "aws_dynamodb_table" "poi_table" {
    name = "poi_table"
    billing_mode = "PAY_PER_REQUEST"
    hash_key = "id"
    
    attribute {
        name = "id"
        type = "N"
    }
}

resource "aws_dynamodb_table" "traildata_table" {
    name = "traildata_table"
    billing_mode = "PAY_PER_REQUEST"
    hash_key = "id"
    range_key = "timestamp"
    
    attribute {
        name = "id"
        type = "N"
    }

    attribute {
        name = "timestamp"
        type = "S"
    }
}

#Sample Data
variable "sampledata" {
  type = list(object({
    id = string
    timestamp = string
  }))
  default = [
    { id = "1",    timestamp = "2024-01-30 06:42:00" },
    { id = "2",    timestamp = "2024-01-30 07:38:00" },
    { id = "3",      timestamp = "2024-01-30 08:01:00" },
    { id = "2",    timestamp = "2024-01-30 08:28:00" },
    { id = "3",      timestamp = "2024-01-30 09:19:00" },
    { id = "1",    timestamp = "2024-01-30 09:43:00" },
    { id = "2",    timestamp = "2024-01-30 10:40:00" },
    { id = "4",timestamp = "2024-01-30 10:45:00" },
    { id = "5",  timestamp = "2024-01-30 11:45:00" },
    { id = "5",  timestamp = "2024-01-30 12:18:00" },
    { id = "6",       timestamp = "2024-01-30 13:01:00" },
    { id = "7",  timestamp = "2024-01-30 13:37:00" },
    { id = "8", timestamp = "2024-01-30 13:54:00" },
    { id = "1",    timestamp = "2024-01-30 14:14:00" },
    { id = "8", timestamp = "2024-01-30 14:47:00" },
    { id = "4",timestamp = "2024-01-30 15:42:00" }
  ]
}

#Test data should be removed
resource "aws_dynamodb_table_item" "items" {
    depends_on = [
        aws_dynamodb_table.traildata_table
    ]

    for_each   = { for idx, item in var.sampledata : idx => item }

    table_name = aws_dynamodb_table.traildata_table.name
    hash_key = aws_dynamodb_table.traildata_table.hash_key
    range_key  = "timestamp"

    item = jsonencode({
        "id": {"N": each.value.id},
        "timestamp": {"S": each.value.timestamp}
    })
}