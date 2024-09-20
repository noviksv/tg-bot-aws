resource "aws_dynamodb_table" "weather_bot_settings" {
  name         = "weather_bot_settings"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "chat_id"

  attribute {
    name = "chat_id"
    type = "S"
  }

  tags = {
    Name        = "WeatherBotSettings"
    Environment = "Dev"
  }
}

