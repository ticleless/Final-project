data "archive_file" "alarm_lambda_zip" {
  type = "zip"

  source_file  = "../lambda-alarm/handler.py"
  output_path = "${path.module}/alarm-handler.zip"
}

module "lambda" {
  source = "terraform-aws-modules/lambda/aws"

  function_name = "alarm-lambda"
  description   = "Send Discord Webhoook"
  handler       = "handler.lambda_handler" 
  runtime       = "python3.8"
  create_package      = false

  local_existing_package = "${data.archive_file.alarm_lambda_zip.output_path}"
  environment_variables = {
      HOOK_URL = var.HookUrl
  }
 
    tags = {
    Name = "alarm-lambda-tag"
  }

}

resource "aws_iam_role_policy_attachment" "alarm_lambda_policy" {
  role       = module.lambda.lambda_role_name
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3FullAccess"
}

resource "aws_s3_bucket_notification" "alarm_lambda_trigger" {
  bucket = aws_s3_bucket.main.id
  lambda_function {
    lambda_function_arn = module.lambda.lambda_function_arn
    events              = ["s3:ObjectCreated:*", "s3:ObjectRemoved:*"]

  }
}
resource "aws_lambda_permission" "s3_to_lambda" {
  statement_id  = "AllowS3Invoke"
  action        = "lambda:InvokeFunction"
  function_name = module.lambda.lambda_function_name
  principal     = "s3.amazonaws.com"
  source_arn    = "arn:aws:s3:::${aws_s3_bucket.main.id}"
}