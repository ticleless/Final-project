data "archive_file" "lambda_zip" {
  type = "zip"

  source_file  = "../trigger-lambda/handler.py"
  output_path = "${path.module}/handler.zip"
}

//Define lambda function
resource "aws_lambda_function" "app" {
  function_name = "trigger-lambda"
  description = "trigger-lambda"
  filename      = data.archive_file.lambda_zip.output_path

  runtime = "python3.9"
  handler = "handler.lambda_handler"

  source_code_hash = data.archive_file.lambda_zip.output_base64sha256

  role = aws_iam_role.lambda_exec.arn
  depends_on = [aws_cloudwatch_log_group.lambda_log]

  environment {
    variables = {
      HOOK_URL = var.HookUrl
    }
  }
}

resource "aws_cloudwatch_log_group" "lambda_log" {
  name = "/aws/lambda/trigger-lambda"

  retention_in_days = 7
}

resource "aws_iam_role" "lambda_exec" {
  name = "serverless_lambda"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Sid    = ""
      Principal = {
        Service = "lambda.amazonaws.com"
      }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_policy" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

// API Gateway stuff

module "api_gateway" {
  source = "terraform-aws-modules/apigateway-v2/aws"

  name          = "trigger-lambda-APIGateway"
  description   = "My awesome HTTP API Gateway"
  protocol_type = "HTTP"
  create_api_domain_name           = false

integrations = {
  "$default" = {
    lambda_arn = aws_lambda_function.app.invoke_arn
    payload_format_version = "2.0"
  }
}

}
resource "aws_lambda_permission" "api_gw" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.app.function_name
  principal     = "apigateway.amazonaws.com"

  source_arn = "${module.api_gateway.apigatewayv2_api_execution_arn}/*"
}


resource "aws_iam_role_policy_attachment" "terraform_lambda_iam_policy_kinesis_execution" {
  role = "${aws_iam_role.lambda_exec.id}"
  policy_arn = "arn:aws:iam::aws:policy/AmazonKinesisFullAccess"

}

data "external" "env" { 
  program = ["${path.module}/env.sh"] 
} 
