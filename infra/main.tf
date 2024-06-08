provider "aws" {
  region = "eu-north-1" # replace with your desired AWS region
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