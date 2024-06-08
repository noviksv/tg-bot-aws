provider "aws" {
  region = "eu-north-1" # replace with your desired AWS region
}

variable "bot_token" {
  description = "The bot token"
  type        = string
}

variable "bot_chat_id" {
  description = "The bot chat ID"
  type        = string
}

variable "weather_api_token" {
  description = "API key to weather service"
  type        = string
}


data "archive_file" "lambda_zip" {
  type        = "zip"
  source_file = "lambda_function.py" # your Python lambda function file
  output_path = "lambda_function_payload.zip"
}

resource "aws_lambda_function" "example" {
  function_name = "example_lambda"

  filename      = data.archive_file.lambda_zip.output_path
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256

  handler = "lambda_function.lambda_handler" # replace with the path to your Lambda function handler
  runtime = "python3.12"    # replace with your Lambda function's runtime
  layers = ["arn:aws:lambda:eu-north-1:437823987706:layer:python-bot-layer:1"]

  environment {
    variables = {
      BOT_TOKEN   = var.bot_token
      BOT_CHAT_ID = var.bot_chat_id
      WEATHER_API_TOKEN = var.weather_api_token
    }
  }

  role = aws_iam_role.example.arn
}

resource "aws_iam_role" "example" {
  name = "example_role"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}

resource "aws_cloudwatch_event_rule" "every_day_at_5_am_utc" {
  name                = "every-day-at-5-am-utc"
  description         = "Fires every day at 5 AM UTC"
  schedule_expression = "cron(0 5 * * ? *)"
}

resource "aws_cloudwatch_event_target" "send_weather_update" {
  rule      = aws_cloudwatch_event_rule.every_day_at_5_am_utc.name
  target_id = "sendWeatherUpdate"
  arn       = aws_lambda_function.example.arn
}

resource "aws_lambda_permission" "allow_cloudwatch" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.example.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.every_day_at_5_am_utc.arn
}