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
  source_file = "../src/lambda_function.py" # your Python lambda function file
  output_path = "lambda_function_payload.zip"
}

