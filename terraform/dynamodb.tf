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