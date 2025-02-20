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
        type = "N"
    }
}

#Sample Data
variable "sampledata" {
  type = list(object({
    id = string
    timestamp = string
  }))
  default = [
    { id = "1", timestamp = "1513865559" },
    { id = "1", timestamp = "1474924084" },
    { id = "7", timestamp = "1658847995" },
    { id = "2", timestamp = "1715745792" },
    { id = "3", timestamp = "1516839578" },
    { id = "10", timestamp = "1609106509" },
    { id = "8", timestamp = "1440214695" },
    { id = "8", timestamp = "1643421386" },
    { id = "9", timestamp = "1649734987" },
    { id = "6", timestamp = "1639909205" },
    { id = "4", timestamp = "1432296713" },
    { id = "1", timestamp = "1625075329" },
    { id = "6", timestamp = "1641247581" },
    { id = "7", timestamp = "1552219145" },
    { id = "4", timestamp = "1604173783" },
    { id = "2", timestamp = "1528135543" },
    { id = "5", timestamp = "1651212097" },
    { id = "3", timestamp = "1605963479" },
    { id = "8", timestamp = "1587332165" },
    { id = "3", timestamp = "1490851076" },
    { id = "6", timestamp = "1591327139" },
    { id = "3", timestamp = "1427706573" },
    { id = "7", timestamp = "1535618834" },
    { id = "8", timestamp = "1701236767" },
    { id = "5", timestamp = "1615394598" },
    { id = "5", timestamp = "1639551974" },
    { id = "10", timestamp = "1549558093" },
    { id = "9", timestamp = "1659330579" },
    { id = "9", timestamp = "1636727753" },
    { id = "8", timestamp = "1687321097" },
    { id = "1", timestamp = "1465672706" },
    { id = "7", timestamp = "1424308143" },
    { id = "1", timestamp = "1678292743" },
    { id = "6", timestamp = "1538544709" },
    { id = "3", timestamp = "1541982364" },
    { id = "9", timestamp = "1659740356" },
    { id = "2", timestamp = "1669783356" },
    { id = "6", timestamp = "1555388834" },
    { id = "5", timestamp = "1632527158" },
    { id = "2", timestamp = "1551456744" },
    { id = "2", timestamp = "1639034412" },
    { id = "4", timestamp = "1729124723" },
    { id = "8", timestamp = "1587173124" },
    { id = "6", timestamp = "1567308169" },
    { id = "3", timestamp = "1570838617" },
    { id = "9", timestamp = "1622129989" },
    { id = "4", timestamp = "1533669619" },
    { id = "3", timestamp = "1674809940" },
    { id = "1", timestamp = "1692943995" },
    { id = "7", timestamp = "1582147974" },
    { id = "1", timestamp = "1725393182" },
    { id = "5", timestamp = "1723987203" },
    { id = "8", timestamp = "1428963503" },
    { id = "5", timestamp = "1488246473" },
    { id = "5", timestamp = "1420319623" },
    { id = "8", timestamp = "1494147211" },
    { id = "4", timestamp = "1690378128" },
    { id = "8", timestamp = "1456312799" },
    { id = "9", timestamp = "1563863509" },
    { id = "4", timestamp = "1494089988" },
    { id = "5", timestamp = "1485984415" },
    { id = "8", timestamp = "1544640299" },
    { id = "1", timestamp = "1689663941" },
    { id = "2", timestamp = "1701120544" },
    { id = "2", timestamp = "1555401093" },
    { id = "4", timestamp = "1457353136" },
    { id = "7", timestamp = "1687258887" },
    { id = "9", timestamp = "1687871426" },
    { id = "2", timestamp = "1710445032" },
    { id = "2", timestamp = "1526040398" },
    { id = "5", timestamp = "1420496307" },
    { id = "6", timestamp = "1619682355" },
    { id = "8", timestamp = "1622109082" },
    { id = "10", timestamp = "1639396866" },
    { id = "2", timestamp = "1698781472" },
    { id = "4", timestamp = "1688995335" },
    { id = "9", timestamp = "1625779573" },
    { id = "1", timestamp = "1518561883" },
    { id = "5", timestamp = "1573589705" },
    { id = "8", timestamp = "1669267103" },
    { id = "10", timestamp = "1731032092" },
    { id = "9", timestamp = "1698823499" },
    { id = "7", timestamp = "1479375321" },
    { id = "1", timestamp = "1573865354" },
    { id = "1", timestamp = "1672019941" },
    { id = "9", timestamp = "1453419744" },
    { id = "3", timestamp = "1603138165" },
    { id = "1", timestamp = "1669576497" },
    { id = "5", timestamp = "1480896926" },
    { id = "4", timestamp = "1462495872" },
    { id = "10", timestamp = "1591152736" },
    { id = "3", timestamp = "1613028780" },
    { id = "7", timestamp = "1561364879" },
    { id = "3", timestamp = "1532706662" },
    { id = "6", timestamp = "1554597970" },
    { id = "9", timestamp = "1734567584" },
    { id = "9", timestamp = "1547197977" },
    { id = "5", timestamp = "1709870371" },
    { id = "5", timestamp = "1438831325" },
    { id = "2", timestamp = "1498640563" }
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
        "timestamp": {"N": each.value.timestamp}
    })
}