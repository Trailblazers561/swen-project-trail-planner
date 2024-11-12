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
    
    attribute {
        name = "id"
        type = "N"
    }
}

#Test data should be removed
resource "aws_dynamodb_table_item" "item1" {
    depends_on = [
        aws_dynamodb_table.traildata_table
    ]
    table_name = aws_dynamodb_table.traildata_table.name
    hash_key = aws_dynamodb_table.traildata_table.hash_key

    item = jsonencode({
        "id": {"N": "1"},
        "name": {"S": "TRAIL ONE"}
    })
}