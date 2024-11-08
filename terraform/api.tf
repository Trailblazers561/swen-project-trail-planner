resource "aws_api_gateway_rest_api" "ecommerce-api" {
  body = jsonencode({
    openapi = "3.0.1"
    info = {
      title   = "${vars.default_name}_api"
      version = "1.0"
    }

    paths = {
      "/trail_data" = {
        get = {
          x-amazon-apigateway-integration = {
            type                 = "AWS_PROXY"
            httpMethod           = "GET"
            uri                  = "${aws_lambda_function.get_trail_data.invoke_arn}"
            payloadFormatVersion = "2.0"
          }
        }
        post = {
          x-amazon-apigateway-integration = {
            type                 = "AWS_PROXY"
            httpMethod           = "POST"
            uri                  = "${aws_lambda_function.upload_trail_data.invoke_arn}"
            payloadFormatVersion = "2.0"
          }
          responses = {
            "200" = {
              content = {
                "application/json" = {
                  schema = {
                    type = "object"
                  }
                }
              }
              headers = {
                "Access-Control-Allow-Origin" = {
                  schema = {
                    type = "string"
                  }
                }
              }
            }
          }
        }
      }
    }
  })
  name = "${vars.default_name}_api"
}