resource "aws_lambda_function" "weather_bot_lambda" {
  function_name = "weather_bot"

  filename         = data.archive_file.lambda_zip.output_path
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256

  handler = "lambda_function.lambda_handler" # replace with the path to your Lambda function handler
  runtime = "python3.12"                     # replace with your Lambda function's runtime
  layers  = ["arn:aws:lambda:eu-north-1:437823987706:layer:python-bot-layer:1"]

  environment {
    variables = {
      BOT_TOKEN         = var.bot_token
      BOT_CHAT_ID       = var.bot_chat_id
      WEATHER_API_TOKEN = var.weather_api_token
    }
  }

  role = aws_iam_role.weather_bot_lambda.arn
}

resource "aws_iam_role" "weather_bot_lambda" {
  name = "weather_bot_lambda_role"

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

resource "aws_lambda_permission" "allow_cloudwatch" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.weather_bot_lambda.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.every_day_at_5_am_utc.arn
}


resource "aws_iam_policy" "lambda_logs_policy" {
  name        = "lambda_logs_policy"
  description = "Policy for Lambda to create and add logs"
  policy      = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:*"
    }
  ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "lambda_logs_policy_attachment" {
  role       = aws_iam_role.weather_bot_lambda.name
  policy_arn = aws_iam_policy.lambda_logs_policy.arn
}

resource "aws_lambda_permission" "apigw" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.weather_bot_lambda.function_name
  principal     = "apigateway.amazonaws.com"

  # The /*/* portion grants access from any method on any resource
  # within the API Gateway "REST API".
  source_arn = "${aws_api_gateway_rest_api.example.execution_arn}/*/*"
}

