resource "aws_cloudwatch_event_rule" "every_day_at_5_am_utc" {
  name                = "every-day-at-5-am-utc"
  description         = "Fires every day at 5 AM UTC"
  schedule_expression = "cron(0 5 * * ? *)"
}


# Define the event payload
locals {
  event_payload = jsonencode({
    "body" = {
      "message" = {
        "text" = "/weather5"
        "chat" = {
          "id" = var.bot_chat_id
        }
      }
    }
  })
}

resource "aws_cloudwatch_event_target" "send_weather_update" {
  rule      = aws_cloudwatch_event_rule.every_day_at_5_am_utc.name
  target_id = "sendWeatherUpdate"
  arn       = aws_lambda_function.weather_bot_lambda.arn
  input     = local.event_payload
}

